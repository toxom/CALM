// ==== src_modules/servo_control.cpp ====
#include "modules/servo_control.h"
#include <Arduino.h>

ServoControl::ServoControl(int servoPin, int minAngle, int maxAngle) 
    : pin(servoPin), minAngle(minAngle), maxAngle(maxAngle), currentAngle(90) {}

bool ServoControl::init() {
    if (servo.attach(pin)) {
        setAngle(90); // Center position
        Serial.printf("✅ Servo initialized on pin %d\n", pin);
        return true;
    }
    Serial.printf("❌ Servo init failed on pin %d\n", pin);
    return false;
}

void ServoControl::setAngle(int angle) {
    angle = constrain(angle, minAngle, maxAngle);
    servo.write(angle);
    currentAngle = angle;
    delay(15); // Allow servo to move
}

void ServoControl::sweep(int startAngle, int endAngle, int stepDelay) {
    startAngle = constrain(startAngle, minAngle, maxAngle);
    endAngle = constrain(endAngle, minAngle, maxAngle);
    
    if (startAngle < endAngle) {
        for (int angle = startAngle; angle <= endAngle; angle++) {
            setAngle(angle);
            delay(stepDelay);
        }
    } else {
        for (int angle = startAngle; angle >= endAngle; angle--) {
            setAngle(angle);
            delay(stepDelay);
        }
    }
}

void ServoControl::sweepContinuous(int cycles, int stepDelay) {
    for (int i = 0; i < cycles; i++) {
        sweep(minAngle, maxAngle, stepDelay);
        sweep(maxAngle, minAngle, stepDelay);
    }
}

int ServoControl::getCurrentAngle() {
    return currentAngle;
}

void ServoControl::smoothMoveTo(int targetAngle, int stepSize, int stepDelay) {
    targetAngle = constrain(targetAngle, minAngle, maxAngle);
    
    while (currentAngle != targetAngle) {
        if (currentAngle < targetAngle) {
            currentAngle = min(currentAngle + stepSize, targetAngle);
        } else {
            currentAngle = max(currentAngle - stepSize, targetAngle);
        }
        setAngle(currentAngle);
        delay(stepDelay);
    }
}