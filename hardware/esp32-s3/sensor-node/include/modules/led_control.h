// LED Configuration
#define LED_PIN 21
// ==== lib/Hardware/led_control.h ====
#ifndef LED_CONTROL_H
#define LED_CONTROL_H

#include <Arduino.h>

class LEDControl {
private:
    int pin;

public:
    LEDControl(int ledPin);
    void init();
    void on();
    void off();
    void toggle();
    void blink(int count, int duration);
    void blinkPattern(int count, int onTime, int offTime);
    void breathe(int cycles, int speed = 10);
};

#endif