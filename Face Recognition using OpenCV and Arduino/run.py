import cv2
import face_recognition
import numpy as np
import os
import pywhatkit as kit
import serial
import time


print("\n\n🔒 Smart Door Lock System")

arduino = serial.Serial('COM5', 9600)
time.sleep(2)

# Load known faces
known_faces_dir = "C:\\Professional\\Python\\Projects\\Face Recognition using OpenCV and Arduino\\DataBase"
known_face_encodings = []
known_face_names = []

def get_camera_index_by_name(target_name="DroidCam"):
    index = 0
    while index < 10:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # use CAP_DSHOW to avoid lag on Windows
        if cap.isOpened():
            backend_name = cap.getBackendName()
            print(f"Checking camera {index} with backend: {backend_name}")
            ret, frame = cap.read()
            if ret:
                # Optional: you can also try to match the resolution or anything specific
                print(f"Camera {index} is working.")
                return index
        cap.release()
        index += 1
    return None

# Try to find your camera
cam_index = get_camera_index_by_name("DroidCam") or 0  # fallback to 0 if not found
print(f"Using camera index: {cam_index}")

# Now use it in your main code
cap = cv2.VideoCapture(cam_index)


for filename in os.listdir(known_faces_dir):
    if filename.endswith((".jpg", ".png")):
        img_path = os.path.join(known_faces_dir, filename)
        img = face_recognition.load_image_file(img_path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(os.path.splitext(filename)[0])

# Send WhatsApp
def send_whatsapp_msg(name):
    message = f"✅ Access Granted to {name} at {time.strftime('%H:%M:%S')}."
    try:
        kit.sendwhatmsg_instantly("+917307157500", message, wait_time=10, tab_close=True)
        print(f"📲 WhatsApp message sent to admin: {message}")
    except Exception as e:
        print(f"⚠️ Failed to send WhatsApp message: {e}")

# Use webcam or DroidCam (change index to your cam)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

        if best_match_index is not None and matches[best_match_index]:
            name = known_face_names[best_match_index]
            print(f"✅ Access Granted to {name}")
            arduino.write(b'G')
            send_whatsapp_msg(name)
        else:
            print("❌ Access Denied")
            arduino.write(b'D')

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Smart Door", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
