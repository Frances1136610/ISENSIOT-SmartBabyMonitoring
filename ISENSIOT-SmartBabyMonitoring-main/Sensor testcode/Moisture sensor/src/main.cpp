#include <Arduino.h>

//Constants
const uint8_t SENSOR_IN = A0; 
const uint64_t BAUD = 115200;
const float SUPPLYVOLTAGE_V = 4.3; //Measured with DMM

//Function declarations
float adcToVoltage_V(int16_t adc);

void setup() 
{
  pinMode(SENSOR_IN, INPUT);
  Serial.begin(BAUD);
}

uint32_t i = 0;
void loop() 
{
  i++;
  int sensorReading_Raw = analogRead(SENSOR_IN);
  Serial.print(i); 
  Serial.print(", ");
  Serial.print(sensorReading_Raw);
  float sensorReading_V = adcToVoltage_V(sensorReading_Raw);
  Serial.print(", ");
  Serial.println(sensorReading_V);
  delay(500);
}

float adcToVoltage_V(int16_t adc)
{
  return (SUPPLYVOLTAGE_V / 1023.0) * adc;
}

