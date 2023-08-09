#include "Wire.h"

const int MPU_addr = 0x68; // адрес датчика

#define points 4096



void setup() {

  
  Wire.begin(21,22,400000); // 1.8 sec, default 4 s
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

/*
 * 4.5 Register 28 – Accelerometer Configuration
ACCEL_CONFIG
Type: Read/Write
Register 
(Hex)
Register
(Decimal) Bit7 Bit6 Bit5 Bit4 Bit3 Bit2 Bit1 Bit0
1C 28 XA_ST YA_ST ZA_ST AFS_SEL[1:0] -
D


AFS_SEL selects the full scale range of the accelerometer outputs according to the following table.
AFS_SEL Full Scale Range
0 ± 2g
1 ± 4g
2 ± 8g
3 ± 16

Register 27 – Gyroscope Configuration
GYRO_CONFIG
Type: Read/Write
Register 
(Hex)
Register
(Decimal) Bit7 Bit6 Bit5 Bit4 Bit3 Bit2 Bit1 Bit0
1B 27 XG_ST YG_ST ZG_ST FS_SEL[1:0] - - -


FS_SEL selects the full scale range of the gyroscope outputs according to the following table.
FS_SEL Full Scale Range
0 ± 250 °/s
1 ± 500 °/s
2 ± 1000 °/s
3 ± 2000 °/s
 * 
 * 
 */

 
  Serial.begin(230400); //921600 115200 460800 2s 2000000 230400
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);
}

void loop() {

  
  long t1 = millis();

  for(int j=0; j<points; j++){
  
    Wire.beginTransmission(MPU_addr);
    Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_addr, 14, true); // request a total of 14 registers 6 12
    

    for (int k=0; k<14; k++){
      Serial.write(Wire.read());
    }

    Serial.write(0x0d);
    Serial.write(0x0a);
    delayMicroseconds(275); //590 mks for 6 bytes 
    

  }

  long t2 = millis();

  Serial.println(t2-t1);

  digitalWrite(2, !digitalRead(2));
  Serial.println();
}
