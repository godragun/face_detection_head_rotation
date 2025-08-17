# face\_detection\_head\_rotation

This project combines an ESP32-CAM with a servo motor to create a simple face-tracking system. A Python script running on a computer detects a face using the `mediapipe` library and sends commands to an ESP32 microcontroller, which in turn controls a servo to follow the detected face.

-----

## Components

  - **ESP32-CAM Module:** Captures video stream.
  - **Servo Motor:** A standard 9g or similar servo.
  - **Jumper wires and Breadboard:** For connecting the components.
  - **Computer with Python:** Runs the face detection and control script.
  - **Power Supply:** A 5V power supply for the ESP32 and servo.

-----

## Hardware Setup

1.  **Connect the Servo to the ESP32:**

      * **Servo VCC (Red wire):** Connect to the 5V pin on the ESP32.
      * **Servo GND (Brown/Black wire):** Connect to a GND pin on the ESP32.
      * **Servo Signal (Orange/Yellow wire):** Connect to **GPIO 13** on the ESP32.

2.  **Power the ESP32-CAM:**

      * Ensure your ESP32-CAM is correctly powered. If using a USB-to-serial adapter, it can be powered via the adapter. For better performance and to avoid brownouts, it's recommended to use a separate 5V power supply.

-----

## Software Setup

### ESP32 (Arduino IDE)

The ESP32 runs a simple web server that listens for commands to set the servo's angle.

1.  **Open the Arduino IDE.**
2.  **Install Required Libraries:**
      * `ESP32Servo`: Go to `Tools > Manage Libraries` and search for "ESP32Servo" to install it.
      * `WebServer` and `WiFi`: These should be pre-installed with the ESP32 board package.
3.  **Upload the Code:**
      * Open the `esp32_servo_webserver.ino` file in the Arduino IDE.
      * This sketch sets up the ESP32 as a Wi-Fi Access Point (AP) with the SSID "**ESP32-Servo-AP**" and password "**password123**".
      * It listens for HTTP GET requests on the root URL (`/`).
      * The `handleRoot` function checks for an `angle` parameter in the request, and the value is used to set the position of the servo motor connected to `SERVO_PIN` (GPIO 13).
      * Upload the code to your ESP32-CAM board.

### Computer (Python)

The Python script performs face detection and sends commands to the ESP32.

1.  **Install Python Libraries:**

    ```bash
    pip install opencv-python mediapipe requests
    ```

2.  **Configure the `servofacedetection.py` script:**

      * Change the `ESP32_IP` variable to the IP address of your ESP32, which will be `192.168.4.1` by default for the AP mode.
      * Change the `ESP32_CAM_URL` to your specific ESP32-CAM's streaming address. For the ESP32-CAM running a standard example, it's typically `http://192.168.1.100:81/stream`.

3.  **Run the Script:**

    ```bash
    python servofacedetection.py
    ```

-----

## How It Works

1.  **Initialization:**
      * The `esp32_servo_webserver.ino` sketch initializes a web server and a servo object.
      * It starts a Wi-Fi Access Point and prints the assigned IP address.
      * The servo is attached to `SERVO_PIN` (GPIO 13) and set to a starting position of 90 degrees.
2.  **Face Detection:**
      * The Python script `servofacedetection.py` captures a video stream from the ESP32-CAM or a local camera.
      * It uses `mediapipe` to process each frame and detect faces.
      * If a face is detected, it calculates the horizontal position of the face's center.
3.  **Servo Control:**
      * The script calculates the "error," which is the difference between the face's center and the screen's center.
      * If the error is outside a defined "dead zone," a new servo angle is calculated based on this error using a proportional control method.
      * This new angle is clamped to a valid range of 0 to 180 degrees.
4.  **Communication:**
      * The Python script sends an HTTP GET request to the ESP32's web server at the address `http://<ESP32_IP>/?angle=<new_angle>`.
      * The `handleRoot` function on the ESP32 receives this request, extracts the angle value, and commands the servo to move to the new position.
      * If no face is detected, the script gradually returns the servo to its center position (90 degrees).
