import cv2
import time
import smtplib
import threading
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from ultralytics import YOLO
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================
#  CONFIGURATION — loaded from .env
# ============================================================

# --- Model ---
MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")

# --- Email (Gmail) ---
SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL  = os.getenv("RECEIVER_EMAIL")

# --- SMS (Twilio) ---
TWILIO_SID   = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM  = os.getenv("TWILIO_FROM")
ALERT_TO     = os.getenv("ALERT_TO")

# --- Detection settings ---
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.50"))
CONFIRM_FRAMES       = int(os.getenv("CONFIRM_FRAMES", "5"))
ALERT_COOLDOWN       = int(os.getenv("ALERT_COOLDOWN", "60"))

# ============================================================
#  ALERT FUNCTIONS
# ============================================================

def send_email(frame):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "🔥 SMOKE / FIRE DETECTED — Immediate Alert"
        msg['From']    = SENDER_EMAIL
        msg['To']      = RECEIVER_EMAIL
        msg.attach(MIMEText(
            "Smoke or fire was detected by your camera system. See attached snapshot.",
            'plain'
        ))

        # Attach snapshot of the frame
        _, img_encoded = cv2.imencode('.jpg', frame)
        msg.attach(MIMEImage(img_encoded.tobytes(), name='snapshot.jpg'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("[EMAIL] Alert sent successfully!")
    except Exception as e:
        print(f"[EMAIL] Failed to send: {e}")


def send_sms():
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body="ALERT: Smoke or fire detected by your camera system! Check immediately.",
            from_=TWILIO_FROM,
            to=ALERT_TO
        )
        print("[SMS] Alert sent successfully!")
    except Exception as e:
        print(f"[SMS] Failed to send: {e}")


def send_alerts(frame):
    # Run both alerts in background threads so detection doesn't pause
    threading.Thread(target=send_email, args=(frame.copy(),), daemon=True).start()
    threading.Thread(target=send_sms, daemon=True).start()


# ============================================================
#  MAIN DETECTION LOOP
# ============================================================

def main():
    print("Loading model...")
    model = YOLO(MODEL_PATH)
    print(f"Model loaded! Classes: {list(model.names.values())}")

    print("Opening webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam. Check it is connected.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    smoke_frame_count = 0
    last_alert_time   = 0

    print("\nSmoke detection running. Press Q to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Could not read frame from webcam.")
            break

        # --- Run detection ---
        results        = model(frame, verbose=False)[0]
        smoke_detected = False
        label          = ""

        for box in results.boxes:
            label = results.names[int(box.cls)]
            conf  = float(box.conf)

            if conf >= CONFIDENCE_THRESHOLD:
                smoke_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw red bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                # Label with class and confidence
                label_text = f"{label.upper()} {conf:.0%}"
                cv2.rectangle(frame, (x1, y1 - 28),
                              (x1 + len(label_text) * 13, y1), (0, 0, 255), -1)
                cv2.putText(frame, label_text, (x1 + 4, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # --- Consecutive frame confirmation ---
        if smoke_detected:
            smoke_frame_count += 1
        else:
            smoke_frame_count = 0

        # --- Trigger alert after CONFIRM_FRAMES consecutive detections ---
        now = time.time()
        if smoke_frame_count >= CONFIRM_FRAMES and (now - last_alert_time) > ALERT_COOLDOWN:
            print(f"\n{'='*40}")
            print("  SMOKE / FIRE CONFIRMED — SENDING ALERTS!")
            print(f"{'='*40}\n")
            send_alerts(frame)
            last_alert_time   = now
            smoke_frame_count = 0

        # --- Status overlay ---
        if smoke_detected:
            status_text  = f"{label.upper()} DETECTED! ({smoke_frame_count}/{CONFIRM_FRAMES})"
            status_color = (0, 0, 255)
            cv2.rectangle(frame, (0, 0),
                          (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 6)
        else:
            status_text  = "Monitoring... (Press Q to quit)"
            status_color = (0, 200, 0)

        cv2.rectangle(frame, (0, 0), (frame.shape[1], 38), (0, 0, 0), -1)
        cv2.putText(frame, status_text, (10, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, status_color, 2)

        if last_alert_time > 0:
            remaining = max(0, int(ALERT_COOLDOWN - (now - last_alert_time)))
            if remaining > 0:
                cv2.putText(frame, f"Next alert in: {remaining}s",
                            (10, frame.shape[0] - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("Smoke & Fire Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Quitting...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
