#ifndef VTF_DRIVER_H
#define VTF_DRIVER_H

#include "Arduino.h"
#include <Wire.h>
#include "Adafruit_DRV2605.h"

#define TCAADDR0 0x70
#define TCAADDR1 0x74

#define MOTOR0 0
#define MOTOR1 1
#define MOTOR2 2
#define MOTOR3 3
#define MOTOR4 4
#define MOTOR5 5
#define MOTOR6 6
#define MOTOR7 7
#define MOTOR8 8
#define MOTOR9 9
#define MOTOR10 10
#define MOTOR11 11
#define MOTOR12 12

#define RatedVoltage            99
#define OverDriveVoltage        161
#define CompensationDefault      12
#define BackEMFDefault           108

#define Default                  0
#define AutoCalibrate           1

class vtf_driver {
    public:
        vtf_driver(void);
        void change_motor(int motorNum);
        void tcas_set_multi(int* motors);
        void go_multi(int* motors, Adafruit_DRV2605 drv_x);
        void LRA_setup(int motorNum, Adafruit_DRV2605* drv_x, int set_up_type);
        void ERM_setup(int motorNum, Adafruit_DRV2605* drv_x);
        uint8_t get_tcas(int motorNum);
        uint8_t get_tcas_port(int motorNum);
        uint8_t is_LRA(int motorNum);

    private:
};

#endif