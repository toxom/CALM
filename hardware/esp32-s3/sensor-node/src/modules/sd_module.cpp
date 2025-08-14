// ==== src_modules/sd_module.cpp ====
#include "modules/sd_module.h"

SDModule::SDModule(int miso) : misoPin(miso) {}

bool SDModule::testConnection() {
    pinMode(misoPin, INPUT_PULLUP);
    delay(100);
    
    bool cardPresent = !digitalRead(misoPin); // Typically LOW when card present
    
    Serial.printf("SD Card MISO (pin %d): %s\n", misoPin, digitalRead(misoPin) ? "HIGH" : "LOW");
    Serial.printf("Card status: %s\n", cardPresent ? "PRESENT" : "NOT PRESENT");
    
    return cardPresent;
}

void SDModule::printStatus() {
    Serial.println("=== SD Card Test ===");
    testConnection();
    Serial.println("Insert/remove card and reset to test");
}

bool SDModule::isCardPresent() {
    pinMode(misoPin, INPUT_PULLUP);
    delay(10);
    return !digitalRead(misoPin);
}
