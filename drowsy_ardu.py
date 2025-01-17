import cv2
import time
import serial

def sleep_detection_system():
    # Initialize serial communication with Arduino
    try:
        arduino = serial.Serial('/dev/ttyACM0', 9600)  # Adjust the port as needed
        time.sleep(2)  # Wait for the connection to establish
        print("Connected to Arduino")
    except Exception as e:
        print(f"Failed to connect to Arduino: {e}")
        return

    # Load Haar cascades for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    if face_cascade.empty() or eye_cascade.empty():
        print("Error loading Haar cascades. Make sure the XML files are present.")
        return

    cap = cv2.VideoCapture(0)  # Open webcam

    eye_closed_frames = 0
    eye_open_frames = 0
    CLOSED_THRESHOLD = 5  # Number of consecutive frames to detect closed eyes

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))

            # Draw rectangles around the eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            if len(eyes) == 0:
                eye_closed_frames += 1
                eye_open_frames = 0
            else:
                eye_open_frames += 1
                eye_closed_frames = 0

            # Check if eyes are closed for too long
            if eye_closed_frames > CLOSED_THRESHOLD:
                cv2.putText(frame, "DROWSINESS ALERT!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                try:
                    arduino.write(b'ALERT\n')  # Send alert signal to Arduino
                except Exception as e:
                    print(f"Failed to send data to Arduino: {e}")
                print("Sleepy driver detected!")

        # Display the frame with eye tracking
        cv2.imshow('Sleep Detection System', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    arduino.close()

# Run the system
sleep_detection_system()
