/*  BNO085 I2C Testbench
    Shows product IDs, enables multiple reports, prints quaternion + Euler (Y/P/R),
    and raw accel/gyro/mag, linear accel, gravity
*/

// check if proper arduino is being used
#if (defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_LEONARDO) || defined(ARDUINO_AVR_NANO))
  #error "This sketch needs more RAM than classic AVR Uno/Leonardo/Nano. Use a Mega 2560, RP2040, SAMD, ESP32, etc. Alternatively, use the UART-RVC sketch below."
#endif

// libraries
#include <Wire.h>
#include <Adafruit_BNO08x.h>   // need to install "Adafruit BNO08x" via Library Manager

// need to config for our address!!
#define BNO08X_I2C_ADDR 0x4A   // 0x4A default, 0x4B if DI pin is tied high
// Choose report interval (in microseconds) 20000us = 50 Hz
const uint32_t REPORT_US = 20000;

// maybe set I2C clock faster if board supports it
const uint32_t I2C_HZ = 400000; // 100k or 400k

// create driver object; reset pin is optional (-1 if not wired)
#define BNO08X_RESET -1
Adafruit_BNO08x bno08x(BNO08X_RESET);

// reusable storage for incoming reports
sh2_SensorValue_t sensorValue;

// function declarations
void enableDesiredReports();
void printEulerFromQuaternion(float r, float i, float j, float k);
float rad2deg(float r);

// FUNCTIONS

// setup function
void setup() {

    // start serial testbench
    Serial.begin(115200);
    while (!Serial) { delay(10); }
    Serial.println(F("\nBNO085 / BNO08x I2C Testbench"));

     Wire.begin();
        #if defined(ARDUINO_ARCH_ESP32) || defined(ARDUINO_ARCH_RP2040) || defined(ARDUINO_ARCH_SAMD) || defined(ARDUINO_SAM_DUE) || defined(ARDUINO_ARCH_STM32)
            Wire.setClock(I2C_HZ);
        #endif

    Serial.print(F("Initializing BNO08x at I2C 0x"));
    Serial.println(BNO08X_I2C_ADDR, HEX);

    // error checking
    if (!bno08x.begin_I2C(BNO08X_I2C_ADDR)) {  
        Serial.println(F("ERROR: Failed to find BNO08x over I2C."));
        Serial.println(F("Tips:"));
        Serial.println(F("  * Check wiring (VIN/GND/SCL/SDA) and board voltage"));
        Serial.println(F("  * Address is 0x4A by default (0x4B if DI pulled high)"));
        Serial.println(F("  * Uno/Leonardo not supported by this library"));
        while (1) delay(10);
    }
    Serial.println(F("BNO08x Found!"));

    // print product and firmware IDs for sanity checking
    for (int n = 0; n < bno08x.prodIds.numEntries; n++) {
        Serial.print(F("Part "));
        Serial.print(bno08x.prodIds.entry[n].swPartNumber);
        Serial.print(F(" | Version "));
        Serial.print(bno08x.prodIds.entry[n].swVersionMajor); Serial.print('.');
        Serial.print(bno08x.prodIds.entry[n].swVersionMinor); Serial.print('.');
        Serial.print(bno08x.prodIds.entry[n].swVersionPatch);
        Serial.print(F(" | Build "));
        Serial.println(bno08x.prodIds.entry[n].swBuildNumber);
    }

    enableDesiredReports();

    // setup complete, start testing
    Serial.println(F("\nReading events... (move the sensor)"));
}

// testbench loop
void loop() {
    // read new events at ~100 Hz
    delay(10);

    // if sensor reset, re-enable reports
    if (bno08x.wasReset()) {
        Serial.println(F("NOTE: BNO08x reported a reset; re-enabling reports."));
        enableDesiredReports();
    }

    // no new data this iteration
    if (!bno08x.getSensorEvent(&sensorValue)) {
        return; 
    }

    // if new report available, read & print it
    switch (sensorValue.sensorId) {

        // print quaterion value
        case SH2_GAME_ROTATION_VECTOR: {
        // quaternion: real (w) + i*x + j*y + k*z
        float w = sensorValue.un.gameRotationVector.real;
        float x = sensorValue.un.gameRotationVector.i;
        float y = sensorValue.un.gameRotationVector.j;
        float z = sensorValue.un.gameRotationVector.k;

        Serial.print(F("[Quat] w: ")); Serial.print(w, 6);
        Serial.print(F(" x: "));       Serial.print(x, 6);
        Serial.print(F(" y: "));       Serial.print(y, 6);
        Serial.print(F(" z: "));       Serial.println(z, 6);

        printEulerFromQuaternion(w, x, y, z);
        } break;

        // print acceleration value
        case SH2_ACCELEROMETER:
        Serial.print(F("[Accel m/s^2] X: ")); Serial.print(sensorValue.un.accelerometer.x, 3);
        Serial.print(F(" Y: "));              Serial.print(sensorValue.un.accelerometer.y, 3);
        Serial.print(F(" Z: "));              Serial.println(sensorValue.un.accelerometer.z, 3);
        break;

        // print gyro value
        case SH2_GYROSCOPE_CALIBRATED:
        Serial.print(F("[Gyro rad/s] X: ")); Serial.print(sensorValue.un.gyroscope.x, 4);
        Serial.print(F(" Y: "));             Serial.print(sensorValue.un.gyroscope.y, 4);
        Serial.print(F(" Z: "));             Serial.println(sensorValue.un.gyroscope.z, 4);
        break;

        // print magnetuc value
        case SH2_MAGNETIC_FIELD_CALIBRATED:
        Serial.print(F("[Mag uT] X: ")); Serial.print(sensorValue.un.magneticField.x, 2);
        Serial.print(F(" Y: "));         Serial.print(sensorValue.un.magneticField.y, 2);
        Serial.print(F(" Z: "));         Serial.println(sensorValue.un.magneticField.z, 2);
        break;

        // print linear acceleration value
        case SH2_LINEAR_ACCELERATION:
        Serial.print(F("[Linear Accel m/s^2] X: ")); Serial.print(sensorValue.un.linearAcceleration.x, 3);
        Serial.print(F(" Y: "));                    Serial.print(sensorValue.un.linearAcceleration.y, 3);
        Serial.print(F(" Z: "));                    Serial.println(sensorValue.un.linearAcceleration.z, 3);
        break;

        // print gravity value
        case SH2_GRAVITY:
        Serial.print(F("[Gravity m/s^2] X: ")); Serial.print(sensorValue.un.gravity.x, 3);
        Serial.print(F(" Y: "));                Serial.print(sensorValue.un.gravity.y, 3);
        Serial.print(F(" Z: "));                Serial.println(sensorValue.un.gravity.z, 3);
        break;

    default:
      // set up a default case
      break;
    }
}

// if reset occurs, re-enable reports
void enableDesiredReports() {
    Serial.println(F("Enabling reports (50 Hz each)..."));
    bool ok = true;
    ok &= bno08x.enableReport(SH2_GAME_ROTATION_VECTOR, REPORT_US);    // Quaternion
    ok &= bno08x.enableReport(SH2_ACCELEROMETER, REPORT_US);
    ok &= bno08x.enableReport(SH2_GYROSCOPE_CALIBRATED, REPORT_US);
    ok &= bno08x.enableReport(SH2_MAGNETIC_FIELD_CALIBRATED, REPORT_US);
    ok &= bno08x.enableReport(SH2_LINEAR_ACCELERATION, REPORT_US);
    ok &= bno08x.enableReport(SH2_GRAVITY, REPORT_US);

    if (!ok) {
        Serial.println(F("WARNING: Could not enable one or more reports."));
    }
}

/* convert quaternion (w,x,y,z) to Euler yaw/pitch/roll in degrees
   based on standard sequence Z (yaw), Y (pitch), X (roll)
   protect asin() domain with clamp for numerical safety*/
void printEulerFromQuaternion(float w, float x, float y, float z) {
    // Z
    float t0 = +2.0f * (w * z + x * y);
    float t1 = +1.0f - 2.0f * (y * y + z * z);
    float yaw = atan2(t0, t1);                 

    // Y
    float t2 = +2.0f * (w * y - z * x);
    t2 = (t2 > 1.0f) ? 1.0f : t2;
    t2 = (t2 < -1.0f) ? -1.0f : t2;
    float pitch = asin(t2);                    

    // X
    float t3 = +2.0f * (w * x + y * z);
    float t4 = +1.0f - 2.0f * (x * x + y * y);
    float roll = atan2(t3, t4);                

    Serial.print(F("[Euler deg] Yaw: "));   Serial.print(rad2deg(yaw),   2);
    Serial.print(F("  Pitch: "));           Serial.print(rad2deg(pitch), 2);
    Serial.print(F("  Roll: "));            Serial.println(rad2deg(roll), 2);
}

// radians to degree return float function
float rad2deg(float r) { return r * 57.29577951308232f; }
