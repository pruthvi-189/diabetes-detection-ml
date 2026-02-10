// ================================
// L298N Motor Driver 1 (Front Motors)
// ================================
#define IN1 2   // Front-Left Motor
#define IN2 3
#define IN3 4   // Front-Right Motor
#define IN4 5

// ================================
// L298N Motor Driver 2 (Rear Motors)
// ================================
#define IN5 6   // Rear-Left Motor
#define IN6 7
#define IN7 8   // Rear-Right Motor
#define IN8 9

String cmd = "";

// ============================================
// INITIAL SETUP
// ============================================
void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(IN5, OUTPUT);
  pinMode(IN6, OUTPUT);
  pinMode(IN7, OUTPUT);
  pinMode(IN8, OUTPUT);

  stopCar();

  Serial.println("Mecanum Car Ready...");
  Serial.println("Commands: f,b,l,r,s, fr, fl, br, bl, rl, rr");
}

// ============================================
// BASIC MOTOR FUNCTIONS
// ============================================
void frontLeftForward() { digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); }
void frontLeftBackward(){ digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); }

void frontRightForward(){ digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW); }
void frontRightBackward(){digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); }

void rearLeftForward() { digitalWrite(IN5, HIGH); digitalWrite(IN6, LOW); }
void rearLeftBackward(){ digitalWrite(IN5, LOW);  digitalWrite(IN6, HIGH); }

void rearRightForward(){ digitalWrite(IN7, HIGH); digitalWrite(IN8, LOW); }
void rearRightBackward(){digitalWrite(IN7, LOW);  digitalWrite(IN8, HIGH); }

void motorsOff() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  digitalWrite(IN5, LOW); digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW); digitalWrite(IN8, LOW);
}

// ============================================
// MOVEMENT FUNCTIONS
// ============================================

// ---- STOP ----
void stopCar() { motorsOff(); }

// ---- FORWARD ----
void moveForward() {
  frontLeftForward();
  frontRightForward();
  rearLeftForward();
  rearRightForward();
}

// ---- BACKWARD ----
void moveBackward() {
  frontLeftBackward();
  frontRightBackward();
  rearLeftBackward();
  rearRightBackward();
}

// ---- MOVE RIGHT (MECANUM STRAFE) ----
void moveRight() {
  frontLeftForward();
  frontRightBackward();
  rearLeftBackward();
  rearRightForward();
}

// ---- MOVE LEFT (MECANUM STRAFE) ----
void moveLeft() {
  frontLeftBackward();
  frontRightForward();
  rearLeftForward();
  rearRightBackward();
}

// ---- DIAGONAL: FRONT-RIGHT ----
void moveFrontRight() {
  frontLeftForward();
  rearRightForward();
}

// ---- DIAGONAL: FRONT-LEFT ----
void moveFrontLeft() {
  frontRightForward();
  rearLeftForward();
}

// ---- DIAGONAL: BACK-RIGHT ----
void moveBackRight() {
  frontLeftBackward();
  rearRightBackward();
}

// ---- DIAGONAL: BACK-LEFT ----
void moveBackLeft() {
  frontRightBackward();
  rearLeftBackward();
}

// ---- ROTATE LEFT ----
void rotateLeft() {
  frontLeftBackward();
  frontRightForward();
  rearLeftBackward();
  rearRightForward();
}

// ---- ROTATE RIGHT ----
void rotateRight() {
  frontLeftForward();
  frontRightBackward();
  rearLeftForward();
  rearRightBackward();
}


// ============================================
// PROCESS SERIAL CMD
// ============================================
void processCommand(String c) {
  c.toLowerCase(); // remove case sensitivity

  if (c == "f") moveForward();
  else if (c == "b") moveBackward();
  else if (c == "r") moveRight();
  else if (c == "l") moveLeft();
  else if (c == "fr") moveFrontRight();
  else if (c == "fl") moveFrontLeft();
  else if (c == "br") moveBackRight();
  else if (c == "bl") moveBackLeft();
  else if (c == "rl") rotateLeft();
  else if (c == "rr") rotateRight();
  else if (c == "s") stopCar();
  else Serial.println("Unknown command!");

  Serial.print("CMD = "); Serial.println(c);
}

// ============================================
// LOOP (clean)
// ============================================
void loop() {
  if (Serial.available()) {
    cmd = Serial.readStringUntil('\n');
    cmd.trim();
    processCommand(cmd);
  }
}