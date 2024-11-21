// Function definitions
void Move_Forward(int car_speed) {
  digitalWrite(2, HIGH);  // Set pin 2 to HIGH for the motor driver
  analogWrite(5, car_speed);  // Set the speed of the motor
  digitalWrite(4, LOW);  // Set pin 4 to LOW for the motor driver (other direction)
  analogWrite(6, car_speed);  // Set the speed of the other motor
}

void Move_Backward(int car_speed) {
  digitalWrite(2, LOW);  // Set pin 2 to LOW for the motor driver (other direction)
  analogWrite(5, car_speed);  // Set the speed of the motor
  digitalWrite(4, HIGH);  // Set pin 4 to HIGH for the motor driver
  analogWrite(6, car_speed);  // Set the speed of the other motor
}

void Rotate_Left(int car_speed) {
  digitalWrite(2, LOW);  // Set pin 2 to LOW for the motor driver (one direction)
  analogWrite(5, car_speed);  // Set speed for one motor
  digitalWrite(4, LOW);  // Set pin 4 to LOW for the motor driver (other direction)
  analogWrite(6, car_speed);  // Set speed for other motor (rotating in opposite direction)
}

void Rotate_Right(int car_speed) {
  digitalWrite(2, HIGH);  // Set pin 2 to HIGH for the motor driver (other direction)
  analogWrite(5, car_speed);  // Set speed for one motor
  digitalWrite(4, HIGH);  // Set pin 4 to HIGH for the motor driver
  analogWrite(6, car_speed);  // Set speed for other motor (rotating in opposite direction)
}

void STOP() {
  digitalWrite(2, LOW);  // Stop the motor
  analogWrite(5, 0);  // Set motor speed to 0
  digitalWrite(4, HIGH);  // Stop the motor
  analogWrite(6, 0);  // Set motor speed to 0
}

float checkdistance() {
  digitalWrite(12, LOW);  // Send a low pulse to the trigger pin
  delayMicroseconds(2);  // Wait for 2 microseconds
  digitalWrite(12, HIGH);  // Send a high pulse to the trigger pin
  delayMicroseconds(10);  // Wait for 10 microseconds to send the pulse
  digitalWrite(12, LOW);  // Set trigger pin back to low
  float distance = pulseIn(13, HIGH) / 58.00;  // Measure the echo time and calculate distance
  delay(10);  // Small delay to stabilize the sensor
  return distance;  // Return the measured distance
}

// Infrared line tracking
int Left_Tra_Value, Center_Tra_Value, Right_Tra_Value;
int Black = 0;  // Assuming the sensor reads 0 for black and 1 for white
int speed = 100;

void Infrared_Tracing() {
  Left_Tra_Value = digitalRead(7);   // Read left infrared sensor
  Center_Tra_Value = digitalRead(8); // Read center infrared sensor
  Right_Tra_Value = digitalRead(9);  // Read right infrared sensor

  if (Left_Tra_Value != Black && (Center_Tra_Value == Black && Right_Tra_Value != Black)) {
    Move_Forward(120);
  } else if (Left_Tra_Value == Black && (Center_Tra_Value == Black && Right_Tra_Value != Black)) {
    Rotate_Left(80);
  } else if (Left_Tra_Value == Black && (Center_Tra_Value != Black && Right_Tra_Value != Black)) {
    Rotate_Left(120);
  } else if (Left_Tra_Value != Black && (Center_Tra_Value != Black && Right_Tra_Value == Black)) {
    Rotate_Right(120);
  } else if (Left_Tra_Value != Black && (Center_Tra_Value == Black && Right_Tra_Value == Black)) {
    Rotate_Right(80);
  } else if (Left_Tra_Value == Black && (Center_Tra_Value == Black && Right_Tra_Value == Black)) {
    STOP();
  }
}

int module = 1;  // Define the current module (set to 1 for obstacle avoidance, 2 for line tracking)

void setup() {
  pinMode(2, OUTPUT);   // Motor control pins
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(12, OUTPUT);  // Ultrasonic trigger pin
  pinMode(13, INPUT);   // Ultrasonic echo pin

  // Set infrared sensor pins
  pinMode(7, INPUT);  // Left line sensor
  pinMode(8, INPUT);  // Center line sensor
  pinMode(9, INPUT);  // Right line sensor
}

void loop() {
  if (module == 1) {  // Module 1: Obstacle Avoidance
    float distance = checkdistance();  // Continuously check distance
    
    if (distance < 6) {
      // If distance is below 3 cm, stop and handle obstacle
      STOP();
      delay(500);  // Wait a bit before moving backward
      Move_Backward(speed);  // Move backward at full speed
      delay(1000);  // Move backward for 1 second
      STOP();
      delay(500);  // Wait before rotating

      // Rotate either left or right (choose one, or alternate)
      int randomInt = random(0, 2);

      // Call the appropriate function based on the random number
      if (randomInt == 0) {
        Rotate_Left(speed);
      } else {
        Rotate_Right(speed);
      }

      delay(1000);  // Rotate for 1 second
      STOP();
      delay(500);  // Wait before moving forward

      // Move forward after rotating
      Move_Forward(speed);
      delay(1000);  // Move forward for 1 second
    } else {
      // If the distance is above 3 cm, keep moving forward
      Move_Forward(speed);
    }
  }

  else if (module == 2) {  // Module 2: Line Tracking
    Infrared_Tracing();  // Call the line tracking function
  }
}
