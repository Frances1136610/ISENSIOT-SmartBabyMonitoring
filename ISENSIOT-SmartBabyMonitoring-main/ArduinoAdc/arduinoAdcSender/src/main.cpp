#include <Arduino.h>
#include <CRC.h>
#include <AGS02MA.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_BusIO_Register.h>

#include <DHT_U.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>

// Constants
const uint8_t ADC_REQUEST_PIN = 3;
const uint8_t PRESENCE_SENSOR_PIN[3] = {A0, A1, A2};
const uint8_t MOISTURE_SENSOR_PIN = A3;
const uint8_t DHT22_PIN = 2;
const uint8_t ADC_AMOUNT_AVERAGE_READINGS = 10;
const uint8_t ADC_AVERAGING_LOOP_DELAY_MILLIS = 10;
const float SUPPLY_VOLTAGE_V = 4.3; //Measured with DMM
#define BAUDRATE 115200
#define DHTTYPE    DHT22     // DHT 22 (AM2302)
 

AGS02MA AGS(26);
Adafruit_MLX90614 MLX = Adafruit_MLX90614();
DHT_Unified dht(DHT22_PIN, DHTTYPE);

// #define DEBUG


// Function declaration
void irqAdcReq();
float adcToVoltage_V(int16_t adc);
float sensorReading(uint8_t pin, uint8_t k);
void sendAdcReadings(float presenceArray[], int size, float moistureSensor, uint32_t TVOCSensor, float IRTempSensor, float tempSensor, float humSensor);
uint32_t calculateCRC(String sensorReading);
void warmUp();
uint32_t readTVOCSensor();
float readIRTempSensor_C();
// bool checkStateDht22(DHT22_ERROR_t errorCode);
void readDht22(float & t, float & h);

// Globals
bool irqAdcReqStatus = 0;

void setup() 
{
  Serial.begin(BAUDRATE);
  #ifdef DEBUG
    Serial.println("Setup begin"); 
  #endif
  //Setup interrupt
  pinMode(ADC_REQUEST_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ADC_REQUEST_PIN), irqAdcReq, FALLING);
  //Debugging LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  //Initialize Wire
  Wire.begin();
  #ifdef DEBUG
    Serial.println("Setup wire");
  #endif
  //Config TVOC Sensor
  AGS.setPPBMode();
  #ifdef DEBUG
    Serial.println("Setup ppbMode");
  #endif
  //warmUp();
  //Init MLX90614
  __attribute__((unused)) bool t;
  t = MLX.begin();
  #ifdef DEBUG
    Serial.println("Setup mlx begin");
  #endif
  #ifdef DEBUG
    Serial.println(t);
    Serial.println("init finished");
  #endif

  dht.begin();
  #ifdef DEBUG
    Serial.println("Setup end");
  #endif
}

void loop() 
{
  float presenceReading[3];
  int8_t size = ((int) sizeof(presenceReading) / sizeof(presenceReading[0])); // The size of the array gets divided by the size of a single data type, in the case of float (4 bytes): 3 * 4 bytes / 4 = 12 / 4 = 3 
  for(int8_t i = 0; i < size; i++)
  {
    presenceReading[i] = adcToVoltage_V(sensorReading(PRESENCE_SENSOR_PIN[i], ADC_AMOUNT_AVERAGE_READINGS));
  }

  float moistureReading = adcToVoltage_V(sensorReading(MOISTURE_SENSOR_PIN, ADC_AMOUNT_AVERAGE_READINGS));
  int tvocReading = readTVOCSensor();
  float irReading = readIRTempSensor_C();
  float temp, hum = -1.0;
  readDht22(temp, hum);

  #ifdef DEBUG
    Serial.print("readIRTempSensor_C: ");
    Serial.println(irReading);
    Serial.print("tvocReading: ");
    Serial.println(tvocReading);
  #endif
  
  if(1 == irqAdcReqStatus)
  {
    #ifdef DEBUG 
      Serial.println("IRQ registered");
    #endif
    irqAdcReqStatus = 0;
    digitalWrite(LED_BUILTIN, LOW); // Reset led
    detachInterrupt(digitalPinToInterrupt(ADC_REQUEST_PIN)); // Disable interrupt between sending of serial data
    sendAdcReadings(presenceReading, size, moistureReading, tvocReading, irReading, temp, hum); 
    attachInterrupt(digitalPinToInterrupt(ADC_REQUEST_PIN), irqAdcReq, FALLING);
  }
}

void irqAdcReq()
{
  irqAdcReqStatus = 1;
  digitalWrite(LED_BUILTIN, HIGH);
}

void sendAdcReadings(float presenceArray[], int size, float moistureSensor, uint32_t TVOCSensor, float IRTempSensor, float tempSensor, float humSensor)
{   
    
    String moisture = String(moistureSensor, 2);
    float tvocF = (float) TVOCSensor;
    String tvoc = String(tvocF, 2);
    String IrTemp = String(IRTempSensor, 2);
    String temp = String(tempSensor, 2);
    String hum = String(humSensor, 2);

    for(int8_t i = 0; i < size; i++)
    {
      String presence = String(presenceArray[i], 2);
      Serial.print("P"); Serial.print(i); Serial.print(":"); Serial.print(presence); Serial.print(",C:"); Serial.print(calculateCRC(presence), HEX); Serial.print(",");
    }
    Serial.print("M:"); Serial.print(moisture); Serial.print(",C:"); Serial.print(calculateCRC(moisture), HEX);
    Serial.print(",O:"); Serial.print(tvoc); Serial.print(",C:"); Serial.print(calculateCRC(tvoc), HEX);
    Serial.print(",IR:"); Serial.print(IrTemp); Serial.print(",C:"); Serial.print(calculateCRC(IrTemp), HEX);
    Serial.print(",T:"); Serial.print(temp); Serial.print(",C:"); Serial.print(calculateCRC(temp), HEX);
    Serial.print(",H:"); Serial.print(hum); Serial.print(",C:"); Serial.print(calculateCRC(hum), HEX);
    
    Serial.println("");
}

float adcToVoltage_V(int16_t adc)
{
  return (SUPPLY_VOLTAGE_V / 1023.0) * adc;
}

float sensorReading(uint8_t pin, uint8_t k)
{
  float reading = 0;
  for(int i = 0; i < k; i++)
  {
    reading += analogRead(pin);
    delay(ADC_AVERAGING_LOOP_DELAY_MILLIS);
  }
  reading /= k;
  return reading;
}

uint32_t calculateCRC(String sensorReading)
{
  // Convert string to char array and calculate CRC
  char str[24];
  sensorReading.toCharArray(str, 24);
  uint8_t * data = (uint8_t *) &sensorReading[0];

  uint32_t Crc = calcCRC32(data, strlen(str)); // Checked with https://crccalc.com/

  #ifdef DEBUG
    Serial.println("DEBUG Func: calculateCRC:");
    Serial.print("Received: ");
    Serial.print(sensorReading);
    Serial.print(", str: ");
    Serial.print(str);
    Serial.print(", string length: ");
    Serial.print(strlen(str));
    Serial.print(", CRC: ");
    Serial.print(Crc, HEX); 
    Serial.println();
  #endif

  return Crc;
}

void warmUp()
{
  #ifdef DEBUG
    Serial.println("Warming up (1 dot = 5 seconds)");
  #endif
  while (AGS.isHeated() == false)
  {
    delay(5000);
    #ifdef DEBUG
      Serial.print(".");
    #endif
  }
  #ifdef DEBUG
    Serial.print("Heating done");
  #endif
}

uint32_t readTVOCSensor()
{
  uint32_t value = AGS.readPPB();
  return value;
}

float readIRTempSensor_C()
{
  return MLX.readObjectTempC();
}

void readDht22(float & t, float & h)
{
  #ifdef DEBUG 
    Serial.println("DHT22 requesting data...");
  #endif

  sensors_event_t event;
  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) 
  {
    #ifdef DEBUG 
      Serial.println(F("Error reading temperature!"));
    #endif
    t = NAN;
    h = NAN;
    return;
  }
  else 
  {
    #ifdef DEBUG 
      Serial.print(F("Temperature: "));
      Serial.print(event.temperature);
      Serial.println(F("°C"));
    #endif
    t = event.temperature;
  }

  // Get humidity event and print its value.
  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) 
  {
    #ifdef DEBUG 
      Serial.println(F("Error reading humidity!"));
    #endif
    t = NAN;
    h = NAN;
    return;
  }
  else 
  {
    #ifdef DEBUG 
      Serial.print(F("Humidity: "));
      Serial.print(event.relative_humidity);
      Serial.println(F("%"));
    #endif
    h = event.relative_humidity;
    return;
  }
}