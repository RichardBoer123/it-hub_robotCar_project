#ifndef MOVEMENT_H
#define MOVEMENT_H

#include <Arduino.h>

class Movement {
  public:
    Movement(int speed = 100);  // Constructor with default speed
    void forward();
    void backward();
    void rotateLeft();
    void rotateRight();
    void stop();

  private:
    int speed;  // Speed of the motor
};

#endif
