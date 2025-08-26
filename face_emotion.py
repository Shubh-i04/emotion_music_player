# face_emotion.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # keep TF logs quieter

import cv2
from deepface import DeepFace

def detect_emotion():
    cap = cv2.VideoCapture(0)
    detected_emotion = "neutral"  # fallback

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            dominant_emotion = result[0]['dominant_emotion']
            detected_emotion = dominant_emotion
            cv2.putText(frame, f'Emotion: {dominant_emotion}', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        except Exception:
            cv2.putText(frame, "No face detected", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow('Emotion Detection (Press q to confirm)', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected_emotion
