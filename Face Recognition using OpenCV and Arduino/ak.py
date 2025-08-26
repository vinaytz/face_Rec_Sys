import cv2
import face_recognition
import numpy as np
import pyautogui
import os
import pywhatkit as kit
import serial
import time

# Setup Arduino
arduino = serial.Serial('COM5', 9600)
time.sleep(2)

# Load known faces
known_faces_dir = "DataBase"

known_face_encodings = []
known_face_names = []

for filename in os.listdir(known_faces_dir):
    if filename.endswith((".jpg", ".png")):
        img_path = os.path.join(known_faces_dir, filename)
        img = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

def send_whatsapp_msg(name):
    msg = f"✅ Access Granted to {name} at {time.strftime('%H:%M:%S')}."
    try:
        kit.sendwhatmsg_instantly("+917307157500", msg, wait_time=10, tab_close=True)
        print(f"📲 WhatsApp sent: {msg}")
    except Exception as e:
        print(f"⚠️ WhatsApp error: {e}")

# Loop: Take screenshot, process with face_recognition
while True:
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances) if face_distances.size > 0 else None

        if best_match_index is not None and matches[best_match_index]:
            name = known_face_names[best_match_index]
            print(f"✅ Access Granted to {name}")
            arduino.write(b'G')
            send_whatsapp_msg(name)
        else:
            print("❌ Access Denied")
            arduino.write(b'D')

        # Draw box and name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Screen Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
