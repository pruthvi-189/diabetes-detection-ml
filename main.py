#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

// -------------------------------------------------------
// Global Servo Limits, Initial Positions, Smoothing
// -------------------------------------------------------
int SERVO_MIN[6] = {0, 0, 0, 0, 20, 40};        // Min allowed degrees
int SERVO_MAX[6] = {180,180,180,180,180,150}; // Max allowed degrees

int SERVO_POS[6] = {90, 90, 90, 90, 90, 90};   // Current position
int SERVO_TARGET[6] = {90, 90, 90, 90, 90, 90}; // Target position

int SMOOTHING = 1;  // smaller = slower movement, bigger = faster
// -------------------------------------------------------


// Convert degrees to PCA9685 pulse length
int angleToPulse(int ang) {
  return map(ang, 0, 180, 150, 600);
}

// -------------------------------------------------------
// Instead of moving instantly, set a target angle
// -------------------------------------------------------
void setServoTarget(uint8_t servo, int angle) {
  if (servo < 1 || servo > 6) return;
  int index = servo - 1;

  angle = constrain(angle, SERVO_MIN[index], SERVO_MAX[index]);
  SERVO_TARGET[index] = angle;
}

// -------------------------------------------------------
// Smoothly move servos a few degrees each cycle
// -------------------------------------------------------
void updateServos() {
  for (int i = 0; i < 6; i++) {

    if (SERVO_POS[i] == SERVO_TARGET[i]) continue;

    if (SERVO_POS[i] < SERVO_TARGET[i])
      SERVO_POS[i] += SMOOTHING;
    else
      SERVO_POS[i] -= SMOOTHING;

    // Prevent overshoot
    SERVO_POS[i] = constrain(SERVO_POS[i], SERVO_MIN[i], SERVO_MAX[i]);

    int pulse = angleToPulse(SERVO_POS[i]);
    pwm.setPWM(i, 0, pulse);
  }
}

// -------------------------------------------------------
// Initialize all servos to starting angles
// -------------------------------------------------------
void initializeServos() {
  for (int i = 0; i < 6; i++) {
    SERVO_TARGET[i] = SERVO_POS[i];
    int pulse = angleToPulse(SERVO_POS[i]);
    pwm.setPWM(i, 0, pulse);
    delay(20);
  }
}

// -------------------------------------------------------
// Parse commands: s1=90 or s1=90,s2=45,s4=120
// -------------------------------------------------------
void parseSerialCommands(String cmd) {
  cmd += ",";

  while (cmd.length() > 0) {
    int commaIndex = cmd.indexOf(',');
    String token = cmd.substring(0, commaIndex);
    cmd.remove(0, commaIndex + 1);

    token.trim();
    if (token.length() == 0) continue;

    if (token.startsWith("s")) {
      int eqIndex = token.indexOf('=');
      if (eqIndex < 0) continue;

      int servoNum = token.substring(1, eqIndex).toInt();
      int angle    = token.substring(eqIndex + 1).toInt();

      setServoTarget(servoNum, angle);
    }
  }
}

// -------------------------------------------------------
// Setup
// -------------------------------------------------------
void setup() {
  Serial.begin(9600);
  pwm.begin();
  pwm.setPWMFreq(50);

  delay(500);
  initializeServos();

  Serial.println("6-DOF Smooth Servo Controller Ready!");
  Serial.println("Commands:");
  Serial.println("s1=90");
  Serial.println("s1=90,s3=150,s5=45");
}

// -------------------------------------------------------
// Loop (kept clean)
// -------------------------------------------------------
void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    parseSerialCommands(input);
  }

  updateServos();  // Smooth movement engine
  delay(20);       // Controls the smoothness
}