#include <Servo.h>

Servo myServo;
unsigned long lastMoveTime = 0;
int moveInterval = 500;
bool isFwd = true;
bool isFishDetected = false;

void setup() {
  Serial.begin(9600);
  myServo.attach(9);
  stopServo();
}

void stopServo() {
  myServo.write(90);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == '0') {
      isFishDetected = true;
      stopServo(); 
    }
    else if (command == '1') {
      isFishDetected = false;
    }
  }
  
  if (!isFishDetected) {
    unsigned long currentTime = millis();
    if (currentTime - lastMoveTime >= moveInterval) {
      lastMoveTime = currentTime;
      
      if (isFwd) {
        myServo.write(180);
      } else {
        myServo.write(0);
      }
      
      isFwd = !isFwd;
    }
  } else {
    stopServo();
  }
}