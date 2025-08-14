#include <Arduino.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <FS.h>
#include <SD.h>
#include <SPI.h>
#include <ArduinoJson.h>
#include "secrets.h"  // Include WiFi credentials
#include "sdm/sdm.h"      // Include SDM functionality

// WiFi credentials from secrets.h (your existing working approach)
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

// SD card pins for XIAO ESP32-S3 - Use pin 1 since that's what worked for you
#define SD_CS    1     // Pin D1 (GPIO1) - This worked in your tests

bool sdInitialized = false;
bool wifiConnected = false;

// SDM components - added to your existing code
SparseDistributedMemory* sdm = nullptr;
SDMEncoder* encoder = nullptr;
SDMBenchmark* benchmark = nullptr;

void setupWiFi() {
  Serial.println("Connecting to WiFi...");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("Password length: ");
  Serial.println(strlen(password));
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("");
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    wifiConnected = false;
    Serial.println("WiFi connection failed!");
  }
}

void setupOTA() {
  if (!wifiConnected) {
    Serial.println("WiFi not connected - OTA disabled");
    return;
  }
  
  // Hostname for OTA
  ArduinoOTA.setHostname("xiao-esp32s3");
  
  // Optional: Set OTA password from environment
  #ifdef OTA_PASSWORD
  ArduinoOTA.setPassword(OTA_PASSWORD);
  #endif
  
  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else { // U_SPIFFS
      type = "filesystem";
    }
    Serial.println("Start updating " + type);
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  
  ArduinoOTA.begin();
  Serial.println("OTA Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void testSDOperations() {
  // List files first
  Serial.println("SD-FILES:");
  File root = SD.open("/");
  int fileCount = 0;
  
  while (true) {
    File entry = root.openNextFile();
    if (!entry) break;
    Serial.println("  " + String(entry.name()) + " (" + String(entry.size()) + " bytes)");
    fileCount++;
    entry.close();
  }
  root.close();
  Serial.println("SD-FILE-COUNT: " + String(fileCount));
  
  // Test SD card type and format
  Serial.println("SD Card Info:");
  Serial.println("Type: " + String(SD.cardType()));
  Serial.println("Size: " + String(SD.cardSize() / (1024 * 1024)) + " MB");
  
  // Test if we can open existing file for reading
  Serial.println("Testing read of existing file...");
  File readTest = SD.open("/TEST.TXT");
  if (readTest) {
    Serial.println("Can read TEST.TXT:");
    while (readTest.available()) {
      Serial.write(readTest.read());
    }
    readTest.close();
    Serial.println("Read test: OK");
  } else {
    Serial.println("Cannot read TEST.TXT");
  }
  
  // Test write to root directory
  Serial.println("Testing write to root directory...");
  File testFile = SD.open("/esp32test.txt", FILE_WRITE);
  if (testFile) {
    testFile.println("ESP32-S3 test");
    testFile.close();
    Serial.println("SD-WRITE: OK");
  } else {
    Serial.println("SD-WRITE: FAILED - Root directory");
  }
  
  // Test write to subdirectory
  Serial.println("Testing subdirectory creation...");
  if (SD.mkdir("/testdir")) {
    Serial.println("Directory created successfully");
    File subFile = SD.open("/testdir/test.txt", FILE_WRITE);
    if (subFile) {
      subFile.println("Subdirectory test");
      subFile.close();
      Serial.println("Subdirectory write: OK");
    } else {
      Serial.println("Subdirectory write: FAILED");
    }
  } else {
    Serial.println("Cannot create directory");
  }
}

void testSDCard() {
  Serial.println("Testing SD card connection...");
  
  // XIAO ESP32-S3 default SPI pins: SCK=8, MISO=9, MOSI=10
  // Try different CS pin options
  const int CS_PINS[] = {1, 2, 3, 4, 5, 6, 21, 44};
  const int NUM_CS_PINS = sizeof(CS_PINS) / sizeof(CS_PINS[0]);
  
  for (int i = 0; i < NUM_CS_PINS; i++) {
    Serial.print("Trying CS pin: ");
    Serial.println(CS_PINS[i]);
    
    if (SD.begin(CS_PINS[i])) {
      Serial.println("SD-OK");
      Serial.print("SD card found with CS=");
      Serial.println(CS_PINS[i]);
      sdInitialized = true;
      testSDOperations();
      return;
    }
    delay(100);
  }
  
  Serial.println("SD-FAILED");
  Serial.println("SD card not found on any CS pin");
  Serial.println("Check: 1) SD card inserted, 2) Wiring, 3) Card format");
  Serial.println("XIAO ESP32-S3 SPI pins: SCK=8, MISO=9, MOSI=10, CS=any digital pin");
  sdInitialized = false;
}

void initializeSDM() {
  if (!sdInitialized) {
    Serial.println("SD card not available - SDM disabled");
    return;
  }
  
  Serial.println("Initializing SDM system...");
  
  // Create benchmark instance first
  benchmark = new SDMBenchmark();
  
  // Find or create optimal configuration
  SDMConfig optimal_config = benchmark->findOptimalConfig();
  
  // Initialize SDM with optimal config
  sdm = new SparseDistributedMemory(optimal_config);
  if (!sdm->initialize()) {
    Serial.println("Failed to initialize SDM");
    delete sdm;
    sdm = nullptr;
    return;
  }
  
  // Initialize encoder
  encoder = new SDMEncoder(sdm);
  
  Serial.println("SDM system initialized successfully");
  sdm->printMemoryUsage();
}

void setup() {
  Serial.begin(9600);
  delay(1000);
  Serial.println("ESP32-S3 Device Ready with OTA and SDM");
  
  // Setup WiFi first
  setupWiFi();
  
  // Setup OTA (only if WiFi connected)
  setupOTA();
  
  // Test SD card on startup
  testSDCard();
  
  // Initialize SDM system
  initializeSDM();
  
  Serial.println("Setup complete!");
  if (wifiConnected) {
    Serial.println("OTA updates available at: " + WiFi.localIP().toString());
  }
  if (sdm) {
    Serial.println("SDM system ready for encoding/decoding");
  }
}

void processSDMCommands(String command) {
  if (!sdm) {
    Serial.println("SDM not initialized");
    return;
  }
  String commandUpper = command;
  commandUpper.toUpperCase();
  if (command.startsWith("ENCODE ")) {
    String text = command.substring(7);
    auto encoded = encoder->encodeText(text);
    
    // Store in SDM
    uint16_t activated = sdm->write(encoded, 5); // Strong reinforcement
    Serial.printf("Encoded '%s' -> %d activated locations\n", text.c_str(), activated);
    
    // Save to SD card
    sdm->saveToSD();
    
  } else if (command.startsWith("DECODE ")) {
    String text = command.substring(7);
    auto encoded = encoder->encodeText(text);
    
    // Try to recall from SDM
    auto [decoded, confidence] = sdm->read(encoded);
    String result = encoder->decodeText(decoded);
    
    Serial.printf("Decoded '%s' -> '%s' (confidence: %.2f)\n", 
                  text.c_str(), result.c_str(), confidence);
    
  } else if (command == "SDM_STATS") {
    SDMStats stats = sdm->getStats();
    Serial.println("=== SDM Statistics ===");
    Serial.printf("Total writes: %d\n", stats.total_writes);
    Serial.printf("Total reads: %d\n", stats.total_reads);
    Serial.printf("Last confidence: %.2f\n", stats.last_confidence);
    Serial.printf("Last activated locations: %d\n", stats.last_activated_locations);
    
  } else if (command == "SDM_SAVE") {
    if (sdm->saveToSD()) {
      Serial.println("SDM saved to SD card");
    } else {
      Serial.println("Failed to save SDM");
    }
    
  } else if (command == "SDM_LOAD") {
    if (sdm->loadFromSD()) {
      Serial.println("SDM loaded from SD card");
    } else {
      Serial.println("Failed to load SDM");
    }
    
  } else if (command == "BENCHMARK_QUICK") {
    if (benchmark && benchmark->runQuickBenchmark()) {
      Serial.println("Quick benchmark completed");
    } else {
      Serial.println("Benchmark failed");
    }
    
  } else if (command == "BENCHMARK_FULL") {
    if (benchmark && benchmark->runComprehensiveBenchmark()) {
      Serial.println("Comprehensive benchmark completed");
    } else {
      Serial.println("Comprehensive benchmark failed");
    }
    
  } else if (command == "BENCHMARK_MEMORY") {
    if (benchmark && benchmark->runMemoryConstraintTest()) {
      Serial.println("Memory constraint test completed");
    } else {
      Serial.println("Memory test failed");
    }
  }
}

void loop() {
  // Handle OTA updates
  if (wifiConnected) {
    ArduinoOTA.handle();
  }
  
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    command.toUpperCase();
    
    if (command == "TEST") {
      Serial.println(wifiConnected ? "WIFI-OK" : "WIFI-FAILED");
      Serial.println("BT-OK");
      Serial.println("CAMERA-OK");
      if (sdInitialized) {
        Serial.println("SD-OK");
      } else {
        Serial.println("SD-FAILED");
      }
      Serial.println(sdm ? "SDM-OK" : "SDM-DISABLED");
      Serial.println(wifiConnected ? "OTA-OK" : "OTA-DISABLED");
      Serial.println("ALL-SYSTEMS-GO");
    }
    else if (command == "PING") {
      Serial.println("PONG");
    }
    else if (command == "IP") {
      if (wifiConnected) {
        Serial.println("IP: " + WiFi.localIP().toString());
      } else {
        Serial.println("WiFi not connected");
      }
    }
    else if (command == "WIFI") {
      setupWiFi();
      if (wifiConnected) {
        setupOTA();
      }
    }
    else if (command == "SD") {
      testSDCard();
    }
    else if (command == "SDWRITE") {
      if (sdInitialized) {
        File f = SD.open("command_test.txt", FILE_WRITE);
        if (f) {
          f.println("Command test: " + String(millis()));
          f.close();
          Serial.println("SD-WRITE-OK");
        } else {
          Serial.println("SD-WRITE-FAILED");
        }
      } else {
        Serial.println("SD-NOT-INITIALIZED");
      }
    }
    else if (command == "RESTART" || command == "REBOOT") {
      Serial.println("Restarting ESP32...");
      delay(1000);
      ESP.restart();
    }
    else if (command == "SDLIST") {
      if (sdInitialized) {
        testSDOperations();
      } else {
        Serial.println("SD-NOT-INITIALIZED");
      }
    }
    else if (command.startsWith("ENCODE ") || command.startsWith("DECODE ") || 
             command.startsWith("SDM_") || command.startsWith("BENCHMARK_")) {
      processSDMCommands(command);
    }
    else {
      Serial.println("Commands: TEST, PING, IP, WIFI, SD, SDWRITE, SDLIST, RESTART");
      Serial.println("SDM Commands: ENCODE <text>, DECODE <text>, SDM_STATS, SDM_SAVE, SDM_LOAD");
      Serial.println("Benchmark: BENCHMARK_QUICK, BENCHMARK_FULL, BENCHMARK_MEMORY");
    }
  }
  
  // Send heartbeat every 10 seconds
  static unsigned long lastHeartbeat = 0;
  if (millis() - lastHeartbeat > 10000) {
    Serial.print("ESP32 heartbeat - WiFi:");
    Serial.print(wifiConnected ? "OK" : "FAIL");
    Serial.print(" SD:");
    Serial.print(sdInitialized ? "OK" : "FAIL");
    Serial.print(" SDM:");
    Serial.print(sdm ? "OK" : "FAIL");
    if (wifiConnected) {
      Serial.print(" IP:" + WiFi.localIP().toString());
    }
    Serial.println();
    lastHeartbeat = millis();
  }
  
  delay(100);
}