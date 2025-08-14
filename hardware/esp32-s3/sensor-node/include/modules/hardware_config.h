// ==== include/hardware_config.h ====
#ifndef HARDWARE_CONFIG_H
#define HARDWARE_CONFIG_H

// LED Configuration
#define LED_PIN 21

// Camera Configuration
#define CAM_PIN_D0    15
#define CAM_PIN_D1    17
#define CAM_PIN_D2    18
#define CAM_PIN_D3    16
#define CAM_PIN_D4    14
#define CAM_PIN_D5    12
#define CAM_PIN_D6    11
#define CAM_PIN_D7    48
#define CAM_PIN_XCLK  10
#define CAM_PIN_PCLK  13
#define CAM_PIN_VSYNC 38
#define CAM_PIN_HREF  47
#define CAM_PIN_SDA   40
#define CAM_PIN_SCL   39
#define CAM_XCLK_FREQ 20000000

// Servo Configuration
#define SERVO_PIN 7

// I2C LCD Configuration
#define LCD_SDA_PIN 5
#define LCD_SCL_PIN 6
#define LCD_ADDRESS 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

// SD Card Configuration
#define SD_MISO_PIN 8

// Serial Configuration
#define SERIAL_BAUD 115200

#endif

// ==== include/led_control.h ====
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