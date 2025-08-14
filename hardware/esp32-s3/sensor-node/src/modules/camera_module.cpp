// ==== src_modules/camera_module.cpp ====
#include "modules/camera_module.h"
#include "modules/hardware_config.h"

CameraModule::CameraModule() {
    status = CAM_NOT_INITIALIZED;
    sensor = nullptr;
}

bool CameraModule::init() {
    // Configure camera
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = CAM_PIN_D0;
    config.pin_d1 = CAM_PIN_D1;
    config.pin_d2 = CAM_PIN_D2;
    config.pin_d3 = CAM_PIN_D3;
    config.pin_d4 = CAM_PIN_D4;
    config.pin_d5 = CAM_PIN_D5;
    config.pin_d6 = CAM_PIN_D6;
    config.pin_d7 = CAM_PIN_D7;
    config.pin_xclk = CAM_PIN_XCLK;
    config.pin_pclk = CAM_PIN_PCLK;
    config.pin_vsync = CAM_PIN_VSYNC;
    config.pin_href = CAM_PIN_HREF;
    config.pin_sccb_sda = CAM_PIN_SDA;
    config.pin_sccb_scl = CAM_PIN_SCL;
    config.pin_pwdn = -1;
    config.pin_reset = -1;
    config.xclk_freq_hz = CAM_XCLK_FREQ;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 15;
    config.fb_count = 1;

    esp_err_t err = esp_camera_init(&config);
    
    if (err == ESP_OK) {
        status = CAM_INITIALIZED;
        sensor = esp_camera_sensor_get();
        Serial.println("✅ Camera initialized successfully");
        return true;
    } else {
        status = CAM_ERROR;
        Serial.printf("❌ Camera init failed: 0x%x\n", err);
        return false;
    }
}

bool CameraModule::isInitialized() {
    return status == CAM_INITIALIZED;
}

CameraStatus CameraModule::getStatus() {
    return status;
}

camera_fb_t* CameraModule::captureFrame() {
    if (!isInitialized()) return nullptr;
    return esp_camera_fb_get();
}

void CameraModule::releaseFrame(camera_fb_t* frame) {
    if (frame) esp_camera_fb_return(frame);
}

bool CameraModule::testResolution(framesize_t size) {
    if (!isInitialized()) return false;
    
    sensor->set_framesize(sensor, size);
    delay(500);
    
    camera_fb_t* fb = captureFrame();
    if (fb) {
        Serial.printf("Resolution test: %dx%d, %d bytes\n", fb->width, fb->height, fb->len);
        releaseFrame(fb);
        return true;
    }
    return false;
}

void CameraModule::printResolutionTest() {
    Serial.println("=== Camera Resolution Test ===");
    
    Serial.println("Testing QVGA (320x240)...");
    testResolution(FRAMESIZE_QVGA);
    
    Serial.println("Testing VGA (640x480)...");
    testResolution(FRAMESIZE_VGA);
    
    Serial.println("Testing UXGA (1600x1200)...");
    if (testResolution(FRAMESIZE_UXGA)) {
        Serial.println("✅ Maximum resolution supported!");
    } else {
        Serial.println("❌ Maximum resolution failed");
    }
}

bool CameraModule::setFrameSize(framesize_t size) {
    if (!isInitialized()) return false;
    sensor->set_framesize(sensor, size);
    return true;
}

bool CameraModule::setQuality(int quality) {
    if (!isInitialized()) return false;
    sensor->set_quality(sensor, quality);
    return true;
}

void CameraModule::printCameraInfo() {
    if (!isInitialized()) {
        Serial.println("Camera not initialized");
        return;
    }
    
    Serial.println("=== Camera Information ===");
    Serial.printf("Sensor PID: 0x%02X\n", sensor->id.PID);
    Serial.printf("Sensor VER: 0x%02X\n", sensor->id.VER);
    Serial.println("Camera ready for capture");
}