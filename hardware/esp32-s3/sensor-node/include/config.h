#ifndef CONFIG_H
#define CONFIG_H

// Pin Configuration
#define LED_PIN 21

// Parallel LCD pins
#define LCD_RS_PIN 2    // A1
#define LCD_EN_PIN 3    // A2  
#define LCD_D4_PIN 4    // A3
#define LCD_D5_PIN 5    // A4
#define LCD_D6_PIN 6    // A5
#define LCD_D7_PIN 8    // A8

// Rotary Encoder pins
#define ENCODER_SW_PIN 20   // A7 - Button
#define ENCODER_DT_PIN 9    // A9 - Data
#define ENCODER_CLK_PIN 10  // A10 - Clock

// Servo pin
#define SERVO_PIN 1     // A0 (moved to free up pins)

#define SERIAL_BAUD 115200

#endif