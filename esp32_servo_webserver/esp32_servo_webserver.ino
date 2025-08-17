#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// --- AP WiFi Configuration ---
const char* ssid = "ESP32-Servo-AP";
const char* password = "password123";

// --- Servo Configuration ---
const int SERVO_PIN = 13; // GPIO pin the servo is connected to

// --- Global Objects ---
WebServer server(80); // Create a web server object on port 80
Servo myServo;        // Create a servo object

/**
 * @brief Handles incoming web requests to the root URL.
 * Parses the 'angle' parameter to control the servo.
 */
void handleRoot() {
  if (server.hasArg("angle")) {
    int angle = server.arg("angle").toInt();
    myServo.write(angle);
    server.send(200, "text/plain", "Angle set to: " + String(angle));
  } else {
    server.send(400, "text/plain", "Invalid request. Use ?angle=VALUE");
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);

  // --- Initialize Servo ---
  myServo.attach(SERVO_PIN);
  myServo.write(90); // Start at the center position
  Serial.println("Servo initialized.");

  // --- Start AP ---
  Serial.print("Starting AP: ");
  Serial.println(ssid);
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);

  // --- Start Web Server ---
  server.on("/", handleRoot); // Associate the handleRoot function with the root URL
  server.begin();
  Serial.println("HTTP server started.");
}

void loop() {
  server.handleClient(); // Listen for incoming client requests
}
