#include <ESP32Servo.h>

Servo myServo;  

int servoPin = 20;  

void setup() {
  myServo.attach(servoPin);  
}

void loop() {
  // Rotate from 0° to 180°
  for (int angle = 0; angle <= 180; angle++) {
    myServo.write(angle);
    delay(15);  // Adjust speed (lower = faster)
  }

  // Rotate back from 180° to 0°
  for (int angle = 180; angle >= 0; angle--) {
    myServo.write(angle);
    delay(15);
  }
}
