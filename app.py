import os
import time
import io
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from ultralytics import YOLO
from PIL import Image
import cv2

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'Devrim2408')

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Mail config - replace with your real credentials or environment variables
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'extenso.svn@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'iubw ogfd liwi fyst')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Folders and model path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'weapon-detection-v3-best.pt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_VIDEO_FOLDER = os.path.join(BASE_DIR, 'static', 'processed_videos')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_VIDEO_FOLDER, exist_ok=True)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

model = YOLO(MODEL_PATH)

friendly_names = {
    'guns': 'Gun',
    'knife': 'Knife',
}

# Routes

@app.route('/')
@login_required
def home():
    if not current_user.confirmed:
        flash('Please verify your email to access full features.', 'warning')
    return render_template('index.html', user=current_user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].lower()
        name = request.form['name']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email already registered.")

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, name=name, password=hashed_password, confirmed=False)
        db.session.add(new_user)
        db.session.commit()

        token = serializer.dumps(email, salt='email-confirm')
        confirm_url = url_for('confirm_email', token=token, _external=True)
        send_email(email, 'Confirm your Email', f'Please click the link to confirm your email: {confirm_url}')

        flash('A confirmation email has been sent. Please check your inbox.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        flash('The confirmation link has expired.', 'warning')
        return redirect(url_for('signup'))
    except BadSignature:
        flash('Invalid confirmation token.', 'danger')
        return redirect(url_for('signup'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.confirmed = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.confirmed:
                flash('Please confirm your email before logging in.', 'warning')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = serializer.dumps(email, salt='password-reset')
            reset_url = url_for('reset_token', token=token, _external=True)
            send_email(email, 'Password Reset Request', f'Click to reset your password: {reset_url}')
        flash('If your email exists in our system, you will receive a password reset email shortly.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        flash('The password reset link has expired.', 'warning')
        return redirect(url_for('reset_request'))
    except BadSignature:
        flash('Invalid or tampered password reset token.', 'danger')
        return redirect(url_for('reset_request'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        password = request.form.get('password')
        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html')

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to])
    msg.body = body
    mail.send(msg)

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('Please fill all fields.', 'error')
        return redirect(url_for('contact'))

    body = f"Message from {name} <{email}>:\n\n{message}"

    try:
        msg = Message("Contact Form Message", sender=app.config['MAIL_USERNAME'], recipients=['extenso.svn@gmail.com'])
        msg.body = body
        mail.send(msg)
        flash('Message sent successfully!', 'success')
    except Exception as e:
        # In production, log the error; here show generic message
        flash('Error sending message. Please try again later.', 'error')

    return redirect(url_for('contact'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        if file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            video_path = os.path.join(UPLOAD_FOLDER, 'uploaded_video.mp4')
            file.save(video_path)
            print(f"Uploaded video saved at: {video_path}")

            cap = cv2.VideoCapture(video_path)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            output_video_path = os.path.join(PROCESSED_VIDEO_FOLDER, 'processed_video.mp4')
            print(f"Output video path: {output_video_path}")

            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(output_video_path, fourcc, 30, (frame_width, frame_height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                results = model(pil_img)
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x_center, y_center, width, height = box.xywh[0].tolist()
                        conf = box.conf[0].item()
                        cls = int(box.cls[0].item())
                        x = int(x_center - width / 2)
                        y = int(y_center - height / 2)
                        w = int(width)
                        h = int(height)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
                        label = friendly_names.get(result.names[cls].lower(), result.names[cls])
                        cv2.putText(frame, label, (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                out.write(frame)

            cap.release()
            out.release()
            video_url = url_for('static', filename='processed_videos/processed_video.mp4') + '?t=' + str(int(time.time()))
            return jsonify({
            "message": "Video processed successfully",
            "video_url": video_url
            })


        else:
            img = Image.open(io.BytesIO(file.read()))
            results = model(img)
            predictions = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x_center, y_center, width, height = box.xywh[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    class_key = result.names[cls].lower()
                    name = friendly_names.get(class_key, result.names[cls])
                    predictions.append({
                        'name': name,
                        'confidence': conf,
                        'x_center': x_center,
                        'y_center': y_center,
                        'width': width,
                        'height': height
                    })
            return jsonify(predictions)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
