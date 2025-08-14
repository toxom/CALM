// ==== src_modules/lcd_control.cpp ====
#include "modules/lcd_control.h"
#include <Arduino.h>

LCDControl::LCDControl(uint8_t address, int cols, int rows, int sda, int scl) 
    : lcd(address, cols, rows), sdaPin(sda), sclPin(scl), initialized(false) {}

bool LCDControl::init() {
    Wire.begin(sdaPin, sclPin);
    lcd.init();
    lcd.backlight();
    lcd.clear();
    
    // Test if LCD responds
    lcd.setCursor(0, 0);
    lcd.print("LCD Test");
    delay(500);
    lcd.clear();
    
    initialized = true;
    Serial.printf("✅ LCD initialized (SDA:%d, SCL:%d)\n", sdaPin, sclPin);
    return true;
}

void LCDControl::clear() {
    if (initialized) lcd.clear();
}

void LCDControl::backlight(bool on) {
    if (initialized) {
        if (on) lcd.backlight();
        else lcd.noBacklight();
    }
}

void LCDControl::setCursor(int col, int row) {
    if (initialized) lcd.setCursor(col, row);
}

void LCDControl::print(const char* text) {
    if (initialized) lcd.print(text);
}

void LCDControl::print(String text) {
    if (initialized) lcd.print(text);
}

void LCDControl::printf(const char* format, ...) {
    if (!initialized) return;
    
    char buffer[64];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    lcd.print(buffer);
}

void LCDControl::scrollText(String text, int row, int delayMs) {
    if (!initialized || text.length() <= 16) {
        setCursor(0, row);
        print(text);
        return;
    }
    
    for (int i = 0; i <= text.length() - 16; i++) {
        setCursor(0, row);
        print(text.substring(i, i + 16));
        delay(delayMs);
    }
}

void LCDControl::displayCentered(String text, int row) {
    if (!initialized) return;
    
    int padding = (16 - text.length()) / 2;
    setCursor(max(0, padding), row);
    print(text);
}

bool LCDControl::isInitialized() {
    return initialized;
}