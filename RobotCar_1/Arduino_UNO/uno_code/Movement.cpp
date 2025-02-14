#include "Movement.h"
#include <Arduino.h>

// Constructor
Movement::Movement(int initialSpeed) {
  speed = initialSpeed;
}

void Movement::forward() {
  digitalWrite(2, HIGH);
  analogWrite(5, speed);
  digitalWrite(4, LOW);
  analogWrite(6, speed);
  Serial.println("Moving forward");
}

void Movement::backward() {
  digitalWrite(2, LOW);
  analogWrite(5, speed);
  digitalWrite(4, HIGH);
  analogWrite(6, speed);
  Serial.println("Moving backward");
}

void Movement::rotateLeft() {
  digitalWrite(2, LOW);
  analogWrite(5, speed);
  digitalWrite(4, LOW);
  analogWrite(6, speed);
  Serial.println("Rotating left");
}

void Movement::rotateRight() {
  digitalWrite(2, HIGH);
  analogWrite(5, speed);
  digitalWrite(4, HIGH);
  analogWrite(6, speed);
  Serial.println("Rotating right");
}

void Movement::stop() {
  digitalWrite(2, LOW);
  analogWrite(5, 0);
  digitalWrite(4, LOW);
  analogWrite(6, 0);
  Serial.println("Stopping");
}
