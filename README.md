# 🔥 Smoke & Fire Detection System

> Real-time smoke and fire detection using YOLOv8 — with instant Email + SMS alerts.

---

## What it does

This system watches your webcam in real time, runs a custom-trained **YOLOv8** model on every frame, and the moment it confirms smoke or fire — it instantly sends you:
- 📧 An **email alert** with a snapshot of what was detected
- 📱 An **SMS alert** to your phone via Twilio

Smart enough to avoid false alarms — detection only triggers after **5 consecutive frames** of confirmed smoke/fire.

---

## Demo

```
Webcam feed → YOLOv8 model → Consecutive frame check → Alert!
                                      ↓
                          📧 Email with snapshot
                          📱 SMS to your phone
```

---

## Features

- 🎯 **Custom YOLOv8 model** trained specifically for smoke & fire detection
- 🔁 **Consecutive frame confirmation** — 5 frames required before alerting (no false alarms)
- 📸 **Email with snapshot** — see exactly what triggered the alert
- 📲 **SMS alert** via Twilio simultaneously
- ⏱ **60-second cooldown** between alerts to avoid notification spam
- 🧵 **Threaded alerts** — detection never pauses while sending notifications
- 🟥 **Visual overlay** — live bounding boxes, confidence scores, and status bar on screen

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Object Detection | YOLOv8 (Ultralytics) |
| Computer Vision | OpenCV |
| SMS Alerts | Twilio API |
| Email Alerts | Gmail SMTP + Python smtplib |
| Language | Python |

---

## Project Structure

```
smoke_fire_detector/
├── detect.py          # Main detection script
├── best.pt            # Trained YOLOv8 model weights
├── requirements.txt   # Dependencies
└── README.md
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/kashviagrawal04/smoke-fire-detector.git
cd smoke-fire-detector
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your credentials

Open `detect.py` and fill in the `CONFIGURATION` section:

```python
# Email (Gmail)
SENDER_EMAIL    = "your_email@gmail.com"
SENDER_PASSWORD = "your_gmail_app_password"   # NOT your real password
RECEIVER_EMAIL  = "alert_receiver@gmail.com"

# SMS (Twilio)
TWILIO_SID   = "your_twilio_sid"
TWILIO_TOKEN = "your_twilio_token"
TWILIO_FROM  = "+1xxxxxxxxxx"    # your Twilio number
ALERT_TO     = "+91xxxxxxxxxx"   # your mobile number
```

### 4. Get a Gmail App Password
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → App Passwords
3. Generate password for "Mail"
4. Paste it as `SENDER_PASSWORD`

### 5. Get Twilio credentials (free)
1. Sign up at [twilio.com](https://twilio.com) (free trial)
2. Get your Account SID, Auth Token, and a Twilio phone number
3. Paste them in the config section

---

## Run

```bash
python detect.py
```

Press **Q** to quit the detection window.

---

## How It Works

```
1. Webcam opens (640x480)
2. Every frame → YOLOv8 inference
3. Detection confidence must be ≥ 50%
4. Smoke/fire must appear in 5 consecutive frames
5. Alert triggered → email (with snapshot) + SMS sent in background threads
6. 60-second cooldown before next alert
```

---

## Detection Settings (tunable)

| Setting | Default | Description |
|--------|---------|-------------|
| `CONFIDENCE_THRESHOLD` | 0.50 | Min confidence to count as detection |
| `CONFIRM_FRAMES` | 5 | Consecutive frames before alert |
| `ALERT_COOLDOWN` | 60s | Wait time between alerts |

---

## ⚠️ Important

> Never commit real credentials to GitHub. Use environment variables or a `.env` file for production use.

Add a `.env` file and use `python-dotenv` to load credentials safely:
```bash
pip install python-dotenv
```

---

## Built With

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [Twilio](https://twilio.com)
- Python `smtplib` for email

