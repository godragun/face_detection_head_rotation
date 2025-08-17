import cv2
import mediapipe as mp
import requests
import time

# ===== CONFIGURATION =====
ESP32_IP = "192.168.4.1"  # Default IP for ESP32 soft AP
ESP32_URL = f"http://{ESP32_IP}/"
ESP32_CAM_URL = "http://192.168.1.100:81/stream" # Change to your ESP32-CAM stream
CENTER_DEAD_ZONE = 40  # Pixels from center to consider as "CENTER"

# --- Mediapipe Face Detection Setup ---
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

# --- Camera Setup ---
cap = cv2.VideoCapture(ESP32_CAM_URL)
if not cap.isOpened():
    print(f"Warning: Could not open ESP32-CAM stream at {ESP32_CAM_URL}.")
    print("Attempting to use default laptop camera (index 0).")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open any camera. Exiting.")
        exit()

# --- State variables for servo control ---
last_angle = 90
servo_angle = 90

def set_servo_angle(angle):
    """Sends the desired angle to the ESP32 server."""
    global last_angle
    try:
        # Send a GET request with the angle
        response = requests.get(ESP32_URL, params={'angle': angle}, timeout=1)
        if response.status_code == 200:
            print(f"Successfully set angle to {angle}")
            last_angle = angle
        else:
            print(f"Failed to set angle. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to ESP32: {e}")

# Set initial position to center
set_servo_angle(90)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        time.sleep(1) # Wait a bit before trying again
        continue

    # Flip the frame horizontally for a more intuitive mirror-like effect
    frame = cv2.flip(frame, 1)

    # Convert the BGR image to RGB for mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to find faces
    face_results = face_detection.process(rgb_frame)

    frame_height, frame_width, _ = frame.shape
    screen_center_x = frame_width // 2

    if face_results.detections:
        # Get the first detected face
        detection = face_results.detections[0]
        mp_draw.draw_detection(frame, detection)

        # Get the bounding box of the face
        bboxC = detection.location_data.relative_bounding_box
        face_center_x = int((bboxC.xmin + bboxC.width / 2) * frame_width)

        # --- Servo Control Logic ---
        error = face_center_x - screen_center_x

        # Move servo only if the face is outside the dead zone
        if abs(error) > CENTER_DEAD_ZONE:
            # Proportional control: further away moves it more
            # Adjust the scaling factor (e.g., 0.1) to change sensitivity
            adjustment = error * 0.1
            servo_angle = last_angle - adjustment
        else:
            # If in the center, gradually move back to 90 degrees
            servo_angle = last_angle * 0.95 + 90 * 0.05

        # Clamp the angle to the valid servo range [0, 180]
        servo_angle = max(0, min(180, int(servo_angle)))

        # Send the new angle to the servo if it has changed significantly
        if abs(servo_angle - last_angle) > 2: # Only update if change is > 2 degrees
            set_servo_angle(servo_angle)

        # Display the current angle on the frame
        cv2.putText(frame, f"Angle: {servo_angle}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.line(frame, (screen_center_x, 0), (screen_center_x, frame_height), (0, 255, 0), 1)
        cv2.line(frame, (face_center_x, 0), (face_center_x, frame_height), (0, 0, 255), 2)

    else:
        # No face detected, gradually return to center
        if abs(90 - last_angle) > 2:
            servo_angle = int(last_angle * 0.95 + 90 * 0.05)
            set_servo_angle(servo_angle)

    # Display the resulting frame
    cv2.imshow("Face Tracking Servo Control", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
print("Cleaning up...")
set_servo_angle(90) # Center the servo on exit
cap.release()
cv2.destroyAllWindows()