// ==== src_modules/debug_utils.cpp ====
#include "debug_utils.h"

void DebugUtils::printHeader(const char* title) {
    Serial.println();
    Serial.println("================================");
    Serial.printf("    %s\n", title);
    Serial.println("================================");
}

void DebugUtils::printSeparator() {
    Serial.println("--------------------------------");
}

void DebugUtils::printSuccess(const char* message) {
    Serial.printf("✅ %s\n", message);
}

void DebugUtils::printError(const char* message) {
    Serial.printf("❌ %s\n", message);
}

void DebugUtils::printInfo(const char* message) {
    Serial.printf("ℹ️  %s\n", message);
}

void DebugUtils::waitForSerial(int timeoutMs) {
    int elapsed = 0;
    while (!Serial && elapsed < timeoutMs) {
        delay(100);
        elapsed += 100;
    }
}

void DebugUtils::printSystemInfo() {
    Serial.println("=== System Information ===");
    Serial.printf("Chip Model: %s\n", ESP.getChipModel());
    Serial.printf("Chip Revision: %d\n", ESP.getChipRevision());
    Serial.printf("CPU Frequency: %d MHz\n", ESP.getCpuFreqMHz());
    Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("Flash Size: %d bytes\n", ESP.getFlashChipSize());
}

void DebugUtils::printMemoryInfo() {
    Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("Min Free Heap: %d bytes\n", ESP.getMinFreeHeap());
    Serial.printf("Max Alloc Heap: %d bytes\n", ESP.getMaxAllocHeap());
}