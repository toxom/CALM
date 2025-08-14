// ==== include/lcd_control.h ====
#ifndef LCD_CONTROL_H
#define LCD_CONTROL_H

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

class LCDControl {
private:
    LiquidCrystal_I2C lcd;
    int sdaPin;
    int sclPin;
    bool initialized;

public:
    LCDControl(uint8_t address, int cols, int rows, int sda, int scl);
    bool init();
    void clear();
    void backlight(bool on = true);
    void setCursor(int col, int row);
    void print(const char* text);
    void print(String text);
    void printf(const char* format, ...);
    void scrollText(String text, int row = 0, int delayMs = 300);
    void displayCentered(String text, int row = 0);
    bool isInitialized();
};

#endif