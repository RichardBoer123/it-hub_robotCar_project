// Include external libraries
#include <WiFiS3.h>
#include <ArduinoJson.h>
#include "Movement.h"

// Define variables
const int robotCarID = 1;
int module = 0;  // Define the current module (set to 1 for obstacle avoidance, 2 for line tracking)
int carSpeed = 100;

// Variables color sensor
#define S0 A2
#define S1 A1
#define S2 A3
#define S3 A0
#define sensorOut 11

// Variables WiFi network
const char *ssid = "IT-HUB-SMARTAUTO";
const char *password = "";

// Replace with your API details
const char* APIserverIP = "192.168.1.103"; // Server IP or domain
const int port = 5000;                 // Port number
const char* endpoint = "/init/";       // API endpoint

// Replace with your device information
const char* deviceName = "Arduino device";

// Call classes
Movement movement(carSpeed);

// Create a server
WiFiServer server(80);

String getDeviceName() {
    // You can define a static device name or use a placeholder
    return "Robot-devicee";
}


float checkdistance() {
  digitalWrite(12, LOW);  // Send a low pulse to the trigger pin
  delayMicroseconds(2);  // Wait for 2 microseconds
  digitalWrite(12, HIGH);  // Send a high pulse to the trigger pin
  delayMicroseconds(10);  // Wait for 10 microseconds to send the pulse
  digitalWrite(12, LOW);  // Set trigger pin back to low
  float distance = pulseIn(13, HIGH) / 58.00;  // Measure the echo time and calculate distance
  delay(10);  // Small delay to stabilize the sensor
  Serial.println(distance);
  return distance;  // Return the measured distance
}

void initRobot() {
  // Create a WiFiClient object
  WiFiClient client;

  // Check if WiFi is still connected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost! Attempting to reconnect...");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }

    Serial.println("\nReconnected to WiFi!");
  }

  // Attempt to connect to the server
  Serial.println("Trying to init robotcar...");
  if (client.connect(APIserverIP, port)) {
    Serial.println("Sucessfully init robot!");

    // Create a JSON object using ArduinoJson
    StaticJsonDocument<200> doc;
    doc["ip"] = WiFi.localIP().toString();
    doc["mac"] = "ABC123";
    doc["deviceName"] = deviceName;
    doc["robotCarID"] = robotCarID;

    // Serialize the JSON object to a string
    String postData;
    serializeJson(doc, postData);

    // Send HTTP POST request
    client.print(String("POST ") + endpoint + " HTTP/1.1\r\n" +
                 "Host: " + APIserverIP + "\r\n" +
                 "Content-Type: application/json\r\n" +
                 "Content-Length: " + postData.length() + "\r\n" +
                 "Connection: close\r\n\r\n" +
                 postData);

    // Wait for response and print it
    Serial.println("Response:");
    while (client.connected() || client.available()) {
      if (client.available()) {
        String line = client.readStringUntil('\n');
        Serial.println(line);
      }
    }

    client.stop(); // Close the connection
  } else {
    Serial.println("Connection to server failed.");
  }
}

void setup() {

  Serial.begin(9600);
  
  if(password == "") {
    WiFi.begin(ssid, NULL);
  }
  else {
    WiFi.begin(ssid, password);
  }

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi... ");
  }
  Serial.println("Connected to WiFi");

  // Print the IP address
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());


  // Set pins motors
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  pinMode(12, OUTPUT);
  pinMode(13, INPUT);

  // Set pins line tracking
  pinMode(7, INPUT);
  pinMode(8, INPUT);
  pinMode(9, INPUT);

  // Set pins color sensor
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(sensorOut, INPUT);

  digitalWrite(S0,HIGH);
  digitalWrite(S1,LOW);
  
  server.begin();
  initRobot();
}

void handleStartRobot(String body) {
  // Check if the body contains valid JSON keys
  if (body.indexOf("LineTracking") >= 0) {
    module = 2;  // Set to Line Tracking
    Serial.println("Switched to Line Tracking mode");
    server.print("HTTP/1.1 200 OK\r\n");
    server.print("Content-Type: application/json\r\n\r\n");
    server.print("{\"message\":\"Line Tracking started!\"}");
  } else if (body.indexOf("ObstacleAvoidance") >= 0) {
    module = 1;  // Set to Obstacle Avoidance
    Serial.println("Switched to Obstacle Avoidance mode");
    server.print("HTTP/1.1 200 OK\r\n");
    server.print("Content-Type: application/json\r\n\r\n");
    server.print("{\"message\":\"Obstacle Avoidance started!\"}");
  } else if (body.indexOf("ColorPath") >= 0) {
    module = 3;  // Set to Obstacle Avoidance
    Serial.println("Switched to Color Path mode");
    server.print("HTTP/1.1 200 OK\r\n");
    server.print("Content-Type: application/json\r\n\r\n");
    server.print("{\"message\":\"Color Path started!\"}");
  } else {
    server.print("HTTP/1.1 400 Bad Request\r\n");
    server.print("Content-Type: application/json\r\n\r\n");
    server.print("{\"error\":\"Invalid mode. Use 'LineTracking' or 'ObstacleAvoidance'.\"}");
  }
}

void handleStopRobot() {
  module = 0;  // Set variable module to 0
  movement.stop();
  Serial.println("Succesfully stopped robotCar");
  server.print("HTTP/1.1 200 OK\r\n");
  server.print("Content-Type: application/json\r\n\r\n");
  server.print("{\"message\":\"Succesfully stopped robotCar!\"}");
}

void loop() {
  // Web server request handling
  WiFiClient client = server.available();
  if (client) {
    Serial.println("New client connected!");

    String request = "";
    while (client.connected() && client.available()) {
      char c = client.read();
      request += c;
    }

    Serial.println("Request received:");
    Serial.println(request);

    // Handle "/startRobot" endpoint
    if (request.startsWith("POST /startRobot")) {
      // Find the body of the request (after \r\n\r\n)
      int bodyStart = request.indexOf("\r\n\r\n") + 4;
      String body = request.substring(bodyStart);

      // Handle the /startRobot logic
      handleStartRobot(body);
    }

    // Handle "/stopRobot" endpoint
    else if (request.startsWith("POST /stopRobot")) {
      handleStopRobot();
    }
    else {
      // If the route is not found, return a 404
      client.print("HTTP/1.1 404 Not Found\r\n");
      client.print("Content-Type: text/plain\r\n\r\n");
      client.print("404: Not Found");
    }

    // Close the connection
    client.stop();
  }

  // Module 1 : 'Object Detection'
  if (module == 1) {
    objectDetection();
  }
  
  // Module 2: 'Line Tracking'
  else if (module == 2) {
    lineTracking("white");
  }

  // Module 3: 'Color Path'
  else if (module == 3) {
    colorPath();
  }
}



void objectDetection() {
  float distance = checkdistance();

  // Checks if the distance is under 20cm
  if (distance < 20) {
    movement.stop();
    delay(500);
    movement.backward();
    delay(500);
    movement.stop();
    delay(500);

    int leftRight = random(0, 2);

    // Call the appropriate function based on the random number
    if (leftRight == 0) {
      movement.rotateLeft();
    } else {
      movement.rotateRight();
    }

    int rotateTime = random(0, 1000);

    delay(rotateTime);
    movement.stop();
    delay(500);
  } else {
    movement.forward();
  }
}

// Infrared line tracking
int Left_Tra_Value, Center_Tra_Value, Right_Tra_Value;

void lineTracking(String color) {
  int White = 1;
  Left_Tra_Value = digitalRead(7);   // Read left infrared sensor
  Center_Tra_Value = digitalRead(8); // Read center infrared sensor
  Right_Tra_Value = digitalRead(9);  // Read right infrared sensor

    Serial.println(Left_Tra_Value);

  if (Left_Tra_Value != White && (Center_Tra_Value == White && Right_Tra_Value != White)) {
    movement.forward();
  } else if (Left_Tra_Value == White && (Center_Tra_Value == White && Right_Tra_Value != White)) {
    movement.rotateRight();
  } else if (Left_Tra_Value == White && (Center_Tra_Value != White && Right_Tra_Value != White)) {
    movement.rotateRight();
  } else if (Left_Tra_Value != White && (Center_Tra_Value != White && Right_Tra_Value == White)) {
    movement.rotateLeft();
  } else if (Left_Tra_Value != White && (Center_Tra_Value == White && Right_Tra_Value == White)) {
    movement.rotateLeft();
  } else if (Left_Tra_Value == White && (Center_Tra_Value == White && Right_Tra_Value == White)) {
    movement.stop();
  }
}

void colorPath() {
  int frequencyR = 0;
  int frequencyG = 0;
  int frequencyB = 0;

  // Reading Red color
  digitalWrite(S2, LOW);
  digitalWrite(S3, LOW);
  frequencyR = pulseIn(sensorOut, LOW);
  Serial.print("R= ");
  Serial.print(frequencyR);
  Serial.print("  ");
  delay(100);

  // Reading Green color
  digitalWrite(S2, HIGH);
  digitalWrite(S3, HIGH);
  frequencyG = pulseIn(sensorOut, LOW);
  Serial.print("G= ");
  Serial.print(frequencyG);
  Serial.print("  ");
  delay(100);

  // Reading Blue color
  digitalWrite(S2, LOW);
  digitalWrite(S3, HIGH);
  frequencyB = pulseIn(sensorOut, LOW);
  Serial.print("B= ");
  Serial.print(frequencyB);
  Serial.print("  ");

  // Determine the dominant color
  String detectedColor;
  if (frequencyR < frequencyG && frequencyR < frequencyB) {
    detectedColor = "RED";
  }
  // Color is "GREEN"
  else if (frequencyG < frequencyR && frequencyG < frequencyB) {
    detectedColor = "GREEN";
    movement.rotateLeft();
    delay(650);
    movement.stop();
    delay(500);
    movement.forward();
    delay(500);
    movement.stop();
  } 
  
  // Color is "BLUE"
  else if (frequencyB < frequencyR && frequencyB < frequencyG) {
    detectedColor = "BLUE";
    movement.forward();
    delay(400);
    movement.stop();
  } else if (frequencyR < 300 && frequencyG < 300 && frequencyB < 300) {
    detectedColor = "WHITE";  // All low means high light reflection
  } else {
    detectedColor = "UNKNOWN"; // Could be a mix or different intensity levels
  }

  Serial.print("Detected Color: ");
  Serial.println(detectedColor);

  delay(100);
}
