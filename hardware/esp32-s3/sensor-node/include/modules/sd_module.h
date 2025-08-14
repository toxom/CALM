// ==== include/sd_module.h ====
#ifndef SD_MODULE_H
#define SD_MODULE_H

#include <Arduino.h>

class SDModule {
private:
    int misoPin;

public:
    SDModule(int miso);
    bool testConnection();
    void printStatus();
    bool isCardPresent();
};

#endif
