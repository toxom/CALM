// ==== include/servo_control.h ====
#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

#include <ESP32Servo.h>

class ServoControl {
private:
    Servo servo;
    int pin;
    int currentAngle;
    int minAngle;
    int maxAngle;

public:
    ServoControl(int servoPin, int minAngle = 0, int maxAngle = 180);
    bool init();
    void setAngle(int angle);
    void sweep(int startAngle, int endAngle, int stepDelay = 50);
    void sweepContinuous(int cycles = 1, int stepDelay = 50);
    int getCurrentAngle();
    void smoothMoveTo(int targetAngle, int stepSize = 1, int stepDelay = 20);
};

#endif