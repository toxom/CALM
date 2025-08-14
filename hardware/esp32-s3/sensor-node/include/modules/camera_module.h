// ==== include/camera_module.h ====
#ifndef CAMERA_MODULE_H
#define CAMERA_MODULE_H

#include <Arduino.h>
#include "esp_camera.h"

enum CameraStatus {
    CAM_NOT_INITIALIZED,
    CAM_INITIALIZED,
    CAM_ERROR
};

class CameraModule {
private:
    camera_config_t config;
    CameraStatus status;
    sensor_t* sensor;

public:
    CameraModule();
    bool init();
    bool isInitialized();
    CameraStatus getStatus();
    camera_fb_t* captureFrame();
    void releaseFrame(camera_fb_t* frame);
    bool testResolution(framesize_t size);
    void printResolutionTest();
    bool setFrameSize(framesize_t size);
    bool setQuality(int quality); // 0-63, lower is better
    void printCameraInfo();
};

#endif