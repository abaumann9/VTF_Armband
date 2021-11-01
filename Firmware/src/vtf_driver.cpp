#include "Arduino.h"
#include <Wire.h>
#include "vtf_driver.h"


Adafruit_DRV2605 drv;

vtf_driver::vtf_driver() {}


/**************************************************************************/
/*!
  @brief Change to a single motor
  @param motorNum Motor to be selected
*/
/**************************************************************************/
void vtf_driver::change_motor(int motorNum){
    byte error;
    byte error1;
    byte error2;

    int tcas = get_tcas(motorNum);
    int port = get_tcas_port(motorNum);

    Wire.beginTransmission(tcas);
    Wire.write(1 << port);
    error = Wire.endTransmission(tcas);
    if (error) {
		Serial.print("Error occured when writing to ");
        if(tcas == TCAADDR0){
            Serial.println("TCAADDR0");
        } else {
            Serial.println("TCAADDR1");
        }
		if (error == 5)
		Serial.println("It was a timeout");
		Serial.println();
	}

    if(tcas == TCAADDR0){
        Wire.beginTransmission(TCAADDR1);
        Wire.write(0);
        error1 = Wire.endTransmission(TCAADDR1);
        if (error1) {
		    Serial.println("Error occured when writing to TCAADDR1");
		if (error1 == 5)
            Serial.println("It was a timeout");
            Serial.println();
        }
	} else {
        Wire.beginTransmission(TCAADDR0);
        Wire.write(0);
        error2 = Wire.endTransmission(TCAADDR0);
        if (error2) {
		    Serial.println("Error occured when writing to TCAADDR0");
		if (error2 == 5)
            Serial.println("It was a timeout");
            Serial.println();
        }
    }
    
}




/**************************************************************************/
/*!
  @brief Select multiple motor drivers at the same time for easy programming
  @param motors Motors to be set, Terminated with a -1
*/
/**************************************************************************/
void vtf_driver::tcas_set_multi(int *motors){
    uint8_t TCAADDR0_Addr = 0;
    uint8_t TCAADDR1_Addr = 0;

    for(int i = 0; i < 14; i++){ 
        if(motors[i] == -1){
            break;
        } else {
            if(get_tcas(motors[i])==TCAADDR1_Addr){
                TCAADDR1_Addr = TCAADDR1_Addr + (1<<get_tcas_port(motors[i]));
            } else {
                TCAADDR0_Addr = TCAADDR0_Addr + (1<<get_tcas_port(motors[i]));
            }
            
        }
    }
    
    Wire.beginTransmission(TCAADDR0);
    Wire.write(TCAADDR0_Addr);
    Wire.endTransmission(TCAADDR0);

    
	Wire.beginTransmission(TCAADDR1);
	Wire.write(TCAADDR1_Addr);
	Wire.endTransmission(TCAADDR1); 

}






/**************************************************************************/
/*!
  @brief Fire multipule motors at once
  @param motors Motors to be fired, Terminated with a -1
  @param drv_x A valid Motor drive initiated in main file (any will do)

*/
/**************************************************************************/
void vtf_driver::go_multi(int *motors, Adafruit_DRV2605 drv_x){
    tcas_set_multi(motors);
    drv_x.go();

}



/**************************************************************************/
/*!
  @brief Return the TCAS Address for a given Motor
  @param motorNum Motor number to return TCAs adress for

*/
/**************************************************************************/
uint8_t vtf_driver::get_tcas(int motorNum){
    if(motorNum < 13){
        if(motorNum == 11 || motorNum == 12 || motorNum == 9 || motorNum == 5 || motorNum == 10){
            return TCAADDR1;
        } else if(motorNum == 7 || motorNum == 8 || motorNum == 4 || motorNum == 2 || motorNum == 8 || motorNum == 6 || motorNum == 3 || motorNum == 1 || motorNum == 0) {
            return TCAADDR0;
        }
    }

    return TCAADDR0;

}


/**************************************************************************/
/*!
  @brief Return the TCAS port for a given motor
  @param motorNum Motor number to return TCAs port for

*/
/**************************************************************************/
uint8_t vtf_driver::get_tcas_port(int motorNum){
    if(motorNum < 13){
        if(motorNum == 2){
            return 0;
        } else if (motorNum == 9 || motorNum == 4){
            return 1;
        } else if (motorNum == 12 || motorNum == 8){
            return 2;
        } else if (motorNum == 11 || motorNum == 7){
            return 3;
        } else if (motorNum == 10 || motorNum == 6){
            return 4;
        } else if (motorNum == 3 || motorNum == 5){
            return 5;
        } else if (motorNum == 1){
            return 6;
        } else if (motorNum == 0){
            return 7;
        }

    }

    return -1;

}


/**************************************************************************/
/*!
  @brief Setup an LRA using the DRV2605 Auto Calibrate. Will only work
         with the LV101040A LRA motor. Params must be changed for other motors
  @param motorNum    Motor to be setup
  @param drv_x       DRV2605 instance for given motorNum initiated in main
  @param set_up_type Determains if Auto Calibration is attempted 
                     or Default values are used

*/
/**************************************************************************/
void vtf_driver::LRA_setup(int motorNum, Adafruit_DRV2605* drv_x, int set_up_type){
    // Serial.println("Starting AUTO Calibration");
    change_motor(motorNum);
    drv_x->begin();
    drv_x->writeRegister8(0x01, 0x00);                                              // out of standby

    drv_x->writeRegister8(DRV2605_REG_RATEDV, RatedVoltage);                        //Set RATED_VOLTAGE ->99
    drv_x->writeRegister8(DRV2605_REG_CLAMPV, OverDriveVoltage);                    //Set OD_CLAMP (Max Allowed Voltage) ->161

    uint8_t feedback_val = 0;
    feedback_val |= (1 << 7);                                                       // Set LRA mode
    feedback_val |= (3 << 4);                                                       // Set Brake Factor to 4x
    feedback_val |= (2 << 2);                                                       // Set Loop Gain to high
    drv_x->writeRegister8(DRV2605_REG_FEEDBACK, feedback_val);

    //Control 1
    uint8_t control_1_val = 0;
    control_1_val |= (1<<7);                                                        //Set Startup Boost
    control_1_val |= (11<<0);                                                       //Set DRIVE_TIME 11    
    drv_x->writeRegister8(DRV2605_REG_CONTROL1, control_1_val);

    //Control 2
    uint8_t control_2_val = 0;
    control_2_val |= (1<<7);                                                        //Set Bidirectional input mode
    control_2_val |= (1<<6);                                                        //Set Brake Stabaliser
    control_2_val |= (3<<4);                                                        //Set SAMPLE_TIME -> 300us
    control_2_val |= (1<<2);                                                        //Set BLANKING_TIME
    control_2_val |= (1<<0);                                                        //Set IDISS_TIME (Current Dissapate Time)
    drv_x->writeRegister8(DRV2605_REG_CONTROL2, control_2_val);

    //Control 3
    uint8_t control_3_val = 0;
    control_3_val |= (2<<6);                                                        //Set NG_THRESH 4%
    control_3_val |= (1<<5);                                                        //For ERMs (Not Important)
    control_3_val |= (1<<0);                                                        //Disables Auto-resonance mode as this is a wideband LRA
    drv_x->writeRegister8(DRV2605_REG_CONTROL3, control_3_val);
    

    //Control 4
    uint8_t control_4_val = 0;
    control_4_val |= (3<<4);                                                        //Set Auto Cal Time to 1000 ms (minimum), 1200 ms (maximum)
    drv_x->writeRegister8(DRV2605_REG_CONTROL4, control_4_val);

    if(set_up_type == AutoCalibrate){
        //Auto Calibraiton
        drv_x->writeRegister8(DRV2605_REG_MODE, 0x07);                               //Auto Calibration Mode

        drv_x->go();                                                                 //Begin Auto Calibration
        while((drv_x->readRegister8(DRV2605_REG_GO)  & 0x01)!=0){                    //Wait For Calibration to finish
            delay(2);
        }                        

        //Check if Calibration was successful
        if((drv_x->readRegister8(DRV2605_REG_STATUS) & (0x08))){                                       
            Serial.println("AUTO Calibration Failed");
            
        }
    } else if (set_up_type == Default){
        drv_x->writeRegister8(DRV2605_REG_AUTOCALCOMP, CompensationDefault);
        drv_x->writeRegister8(DRV2605_REG_AUTOCALEMP, BackEMFDefault);
    }
    
    //Setup as LRA in Predef Mode
    drv_x->selectLibrary(6);
    drv_x->setMode(DRV2605_MODE_INTTRIG); 
    drv_x->setWaveform(0, 0);
	drv_x->go();
    
    /*Use this to see print out of Calibration Values */
    // Serial.print("Motor ");
    // Serial.print(motorNum);
    // Serial.print(" compensation:");
    // Serial.print(drv_x->readRegister8(DRV2605_REG_AUTOCALCOMP));
    // Serial.print(" back-EMF:");
    // Serial.println(drv_x->readRegister8(DRV2605_REG_AUTOCALEMP));
    return;
}

/**************************************************************************/
/*!
  @brief Setup an ERM motor
  @param motorNum Motor to be setup
  @param drv_x DRV2605 instance for given motorNum initiated in main

*/
/**************************************************************************/
void vtf_driver::ERM_setup(int motorNum, Adafruit_DRV2605* drv_x){
    change_motor(motorNum);
    drv_x->begin();
    drv_x->selectLibrary(1);
	drv_x->setMode(DRV2605_MODE_INTTRIG); 
	drv_x->setWaveform(0, 0);
    drv_x->go();
}

uint8_t vtf_driver::is_LRA(int motorNum){
    if(motorNum == 3 || motorNum == 4 ||motorNum == 8 ||motorNum == 9){
        return 0;
    } else {
        return 1;
    }
}