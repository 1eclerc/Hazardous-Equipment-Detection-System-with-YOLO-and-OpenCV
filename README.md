# 🔫 Hazardous Equipment Detection System using YOLO & OpenCV

This project is a **web-based detection system** that uses the YOLOv8 deep learning model and OpenCV to detect situations that contain weapons (e.g., guns, knives) in both **images and videos**. The system includes a **Flask web application** with user authentication, email confirmation, and password reset functionality.

---

## 🚀 Features

- 🔍 Upload image or video to detect weapons
- ✅ Real-time bounding boxes and labels (Gun, Knife)
- 🔒 User login, registration & email confirmation
- 📩 Password reset via email
- 🎥 Video processing and output rendering
- 📊 Prediction results shown with confidence levels

---

## 🧠 Tech Stack

- **Backend**: Python, Flask
- **Detection**: [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- **Frontend**: HTML, Jinja templates
- **Database**: SQLite
- **Authentication**: Flask-Login
- **Email Service**: Flask-Mail
- **Computer Vision**: OpenCV, Pillow

---

## 📁 Project Structure

```
├── app.py                  # Main Flask app
├── model/
│   └── weapon-detection-v3-best.pt
├── templates/              # HTML templates (login, signup, index, etc.)
├── static/
│   └── processed_videos/   # Saved processed videos
├── uploads/                # Uploaded media files
├── users.db                # SQLite database
├── ZIP.zip                 # Project ZIP archive
└── README.md               # Project description (this file)
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```
*(If `requirements.txt` is not available, install manually: Flask, Flask-Login, Flask-Mail, SQLAlchemy, Ultralytics, OpenCV, Pillow)*

3. **Download YOLO model** and place it under `model/` folder as:
```
model/weapon-detection-v3-best.pt
```

4. **Set environment variables** (for email config):
You can do this via `.env` file or in your shell:
```bash
export MAIL_USERNAME="your_email@gmail.com"
export MAIL_PASSWORD="your_app_password"
```

5. **Run the app**:
```bash
python app.py
```

---

## 🔐 Default Routes

| Route              | Description                            |
|-------------------|----------------------------------------|
| `/`               | Home (requires login)                  |
| `/signup`         | User registration                      |
| `/login`          | User login                             |
| `/logout`         | Log out                                |
| `/predict`        | Weapon detection (image or video)      |
| `/about`, `/contact` | Informational pages                |

---

## 📬 Email Functionality

- Upon signup, users receive a **confirmation email**.
- Users can reset their password through email as well.

*(Make sure to use a valid Gmail SMTP setup or your own provider.)*

---

## 📸 Demo

You can upload:
- `.jpg`, `.png`, etc. for images
- `.mp4`, `.avi`, `.mov` for videos

Output video with boxes will be shown and downloadable.

---

## 👥 Team & Contributors

- [@1eclerc](https://github.com/1eclerc)
- [@Engin-Yedirmez](https://github.com/Engin-Yedirmez)
- [@ishowkenobi](https://github.com/ishowkenobi)

## 📄 License

This project is open-source and for educational purposes.

---
