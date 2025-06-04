import serial
import time
import RPi.GPIO as GPIO
import zlib #used for crc
import os 

class AdcData:
    ADC_REQUEST_PIN = 4
    serialPort = "/dev/ttyUSB0"
    serialConnection = None
    presenceSensor = [-1.0, -1.0, -1.0]
    presenceReceivedCrc = [-1, -1, -1]
    crcMatchPresence = [-1, -1, -1]
    moistureSensor = -1.0
    moistureReceivedCrc = -1
    crcMatchMoisture = -1
    tvocSensor = -1.0
    tvocReceivedCRC = -1
    crcMatchTvoc = -1
    irTemperatureSensor = -1.0
    irTemperatureReceivedCRC = -1
    crcMatchIr = -1
    dht22TempSensor = -1.0
    dht22TempReceivedCrc = -1
    crcMatchDht22Temp = -1
    dht22HumSensor = -1.0
    dht22HumReceivedCrc = -1
    crcMatchDht22Hum = -1

    def __init__(self):
        self.setupIrq()
        self.checkSerialConnection()

    def checkSerialConnection(self):
        if not os.path.exists(self.serialPort):
            print("Serial port is not found, reattach USB cable to Arduino")
            quit()
        else:
            self.serialConnection = serial.Serial(   
                port=self.serialPort, 
                baudrate=115200, 
                bytesize=8, 
                timeout=2, 
                stopbits=serial.STOPBITS_ONE
            )
    
    def requestData(self):
        endOfLine = 0
        # Read data until request is over
        while endOfLine != 1:
            GPIO.output(self.ADC_REQUEST_PIN, 0) # Request new data
            time.sleep(0.01)
            GPIO.output(self.ADC_REQUEST_PIN, 1)
            serialString = self.serialConnection.readline() # Read data out of the buffer until a carraige return / new line is found
            serialString = serialString.decode("Ascii")
            splitByComma = serialString.split(',')
            if __debug__:
                print("Length of list: " + str(len(splitByComma)) + ", decoded serialstring: " + serialString)
            if len(splitByComma) >= 12:
                endOfLine = 1
            else:
                endOfLine = 0

        GPIO.output(self.ADC_REQUEST_PIN, 1) # end single request

        # Split received string
        self.splitSensorDataFromSerial(splitByComma)
        # check CRC match
        for i in range(0, 3):
            self.crcMatchPresence[i] = self.checkCrcMatch(self.calculateCrcOfSensorValue_hex(self.presenceSensor[i]), self.presenceReceivedCrc[i])

        self.crcMatchMoisture = self.checkCrcMatch(self.calculateCrcOfSensorValue_hex(self.moistureSensor), self.moistureReceivedCrc)
        self.crcMatchTvoc = self.checkCrcMatch(self.calculateCrcOfSensorValue_hex(self.tvocSensor), self.tvocReceivedCRC)
        self.crcMatchIr = self.checkCrcMatch(self.calculateCrcOfSensorValue_hex(self.irTemperatureSensor), self.irTemperatureReceivedCRC)
        self.crcMatchDht22Temp = self.checkCrcMatch(self.calculateCrcOfSensorValue_hex(self.dht22TempSensor), self.dht22TempReceivedCrc)
        self.crcMatchDht22Hum = self.checkCrcMatch(self.calculateCrcOfSensorValue_hex(self.dht22HumSensor), self.dht22HumReceivedCrc)
        #printing for check
        if __debug__:
            print("presence: {p0}, {p1}, {p2}, moisture {m}, Tvoc {t}, IR {i}, CRC match = {c}".format(p0 = self.presenceSensor[0], p1 = self.presenceSensor[1], p2= self.presenceSensor[2], m = self.moistureSensor, t = self.tvocSensor, i = self.irTemperatureSensor, c =  "True" if (any(self.crcMatchPresence) and self.crcMatchMoisture and self.crcMatchTvoc and self.crcMatchIr) else "False"))

    def getData(self):
        return self.presenceSensor, self.moistureSensor, self.tvocSensor, self.irTemperatureSensor, self.dht22TempSensor, self.dht22HumSensor
        
    def setupIrq(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.ADC_REQUEST_PIN, GPIO.OUT)
        GPIO.output(self.ADC_REQUEST_PIN, 1)

    def splitSensorDataFromSerial(self, split):
        for i in range(0, 3):
            self.presenceSensor[i] = split[i * 2].replace("P{x}:".format(x = i), '').strip()
            self.presenceReceivedCrc[i] = "0x" + split[i * 2 + 1].replace("C:", '').strip().lower()

        self.moistureSensor = split[6].replace("M:", '').strip()
        self.moistureReceivedCrc = "0x" + split[7].replace("C:", '').strip().lower()
        self.tvocSensor = split[8].replace("O:", '').strip()
        self.tvocReceivedCRC = "0x" + split[9].replace("C:", '').strip().lower()
        self.irTemperatureSensor = split[10].replace("IR:", '').strip()
        self.irTemperatureReceivedCRC = "0x" + split[11].replace("C:", '').strip().lower()
        self.dht22TempSensor = split[12].replace("T:", '').strip()
        self.dht22TempReceivedCrc = "0x" + split[13].replace("C:", '').strip().lower()
        self.dht22HumSensor = split[14].replace("H:", '').strip()
        self.dht22HumReceivedCrc = "0x" + split[15].replace("C:", '').strip().lower()

        if __debug__: # Print the contents of the serial data
            print("Split by comma output: %s" % split)
            print("Presence sensor reading: {p0}, {p1}, {p2}".format(p0 = self.presenceSensor[0], p1 = self.presenceSensor[1], p2 = self.presenceSensor[2]))
            print("Presence sensor received CRC: {c0}, {c1}, {c2}".format(c0 = self.presenceReceivedCrc[0], c1 = self.presenceReceivedCrc[1], c2 = self.presenceReceivedCrc[2]))
            print("Moisture sensor reading: " + self.moistureSensor)
            print("Moisture sensor received CRC: " + self.moistureReceivedCrc)
            print("TVOC sensor reading: " + self.tvocSensor)
            print("TVOC sensor received CRC: " + self.tvocReceivedCRC)
            print("IR sensor reading: " + self.irTemperatureSensor)
            print("IR sensor received CRC: " + self.irTemperatureReceivedCRC)
            print("DHT22 temp reading: " + self.dht22TempSensor)
            print("DHT22 temp received CRC: " + self.dht22TempReceivedCrc)
            print("DHT22 hum reading: " + self.dht22HumSensor)
            print("DHT22 hum received CRC: " + self.dht22HumReceivedCrc)

    def checkCrcMatch(self, crc1, crc2):
        if crc1 == crc2:
            if __debug__:
                print("CRC do match, crc1: {fcrc1} = crc2: {fcrc2}".format(fcrc1 = crc1, fcrc2 = crc2))

            return 1
        else:
            if __debug__:
                print("CRC do no match, crc1: {fcrc1} != crc2: {fcrc2}".format(fcrc1 = crc1, fcrc2 = crc2))

            return 0

    def calculateCrcOfSensorValue_hex(self, sensorValue):
        convertedString = sensorValue#str(int((float(sensorValue)) * 100)) # Convert the received value to integer while preserving 2 decimal places by multiplying with 100 and convert back to string value
        byte_data = convertedString.encode('utf-8') # Convert to bytes using UTF-8 encoding
        crc32_value = zlib.crc32(byte_data) # Calculate the CRC32 checksum
        if __debug__:
            print("Calculated CRC: " + str(hex(crc32_value))) # Print the CRC32 value

        return hex(crc32_value)