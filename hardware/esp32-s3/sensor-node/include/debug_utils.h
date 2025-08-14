// ==== include/debug_utils.h ====
#ifndef DEBUG_UTILS_H
#define DEBUG_UTILS_H

#include <Arduino.h>

class DebugUtils {
public:
    static void printHeader(const char* title);
    static void printSeparator();
    static void printSuccess(const char* message);
    static void printError(const char* message);
    static void printInfo(const char* message);
    static void waitForSerial(int timeoutMs = 3000);
    static void printSystemInfo();
    static void printMemoryInfo();
};

#endif