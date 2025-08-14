
// ==== lib/Hardware/led_control.cpp ====
#include "modules/led_control.h"

LEDControl::LEDControl(int ledPin) : pin(ledPin) {}

void LEDControl::init() {
    pinMode(pin, OUTPUT);
    off(); // Start with LED off
}

void LEDControl::on() {
    digitalWrite(pin, LOW); // Assuming active low
}

void LEDControl::off() {
    digitalWrite(pin, HIGH); // Assuming active low
}

void LEDControl::toggle() {
    digitalWrite(pin, !digitalRead(pin));
}

void LEDControl::blink(int count, int duration) {
    for(int i = 0; i < count; i++) {
        on();
        delay(duration);
        off();
        delay(duration);
    }
}

void LEDControl::blinkPattern(int count, int onTime, int offTime) {
    for(int i = 0; i < count; i++) {
        on();
        delay(onTime);
        off();
        delay(offTime);
    }
}

void LEDControl::breathe(int cycles, int speed) {
    for(int cycle = 0; cycle < cycles; cycle++) {
        // Fade in
        for(int brightness = 0; brightness <= 255; brightness += speed) {
            analogWrite(pin, 255 - brightness); // Invert for active low
            delay(10);
        }
        // Fade out
        for(int brightness = 255; brightness >= 0; brightness -= speed) {
            analogWrite(pin, 255 - brightness); // Invert for active low
            delay(10);
        }
    }
    off();
}