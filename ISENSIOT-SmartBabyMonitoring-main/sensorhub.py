#Costum libraries
from Firebase.firebaseSender import FirebaseSender
from ArduinoAdc.ReceiverPi.arduinoAdc import AdcData
from Visualization.influxDBSender import InfluxSender
#Scheduling
import time
from timeloop import Timeloop
from datetime import timedelta
#Checking if there is a internet connection
import socket
#Remaining
import pathlib

#CONTSTANTS
INFLUX_INTERVAL = 1
FIREBASE_INTERVAL = 60

PRESENCE_INTERVAL = 20
PRESENCE_THRESHOLD_V = 3.5

MOISTURE_INTERVAL = 20
MOISTURE_FALL_V = 0.3

IR_INTERVAL = 20
IR_TEMPERATURE_OFFSET_CELSIUS = 10.7
IR_HIGHEST_PERCENTAGE = 10

#Firebase
credPath = str('/home/pi/Documents/ISENSIOT-SmartBabyMonitoring/cred.json')
fireDb = FirebaseSender()
fireDb.setupConnection(credPath)

#InfluxDB
bucket = "isensiot"
org = "isensiot"
token = "aqS3xEhM-DwkuCaAHHKzDzAZXc1bkAlSnQ058gvYzpuSJVRq4rUcdPXAG51t8iQl_q_wMdw3Y5qSwJoCcFOijw=="
url="http://localhost:8086"
influxDb = InfluxSender()
influxDb.setupConnection(bucket, org, token, url)

adc = AdcData() #Create external-ADC object

tl = Timeloop()

timeRuning = 0 #timecounter to check if there is enough info in database to run reoccuring get average tasks 

#InfluxDB update job
@tl.job(interval=timedelta(seconds=INFLUX_INTERVAL))
def influx():
    if __debug__:
        print ("InfluxDB job: {}".format(time.ctime()))

    adc.requestData()
    presenceSensor, moistureSensor, tvocSensor, irSensor, dht22Temp, dht22Hum = adc.getData()
    for i in range(0, 3):
        influxDb.sendData("testing", "testing", "presence{p}".format(p = i), "volts", float(presenceSensor[i]))
    
    influxDb.sendData("testing", "testing", "moisture", "volts", float(moistureSensor))
    influxDb.sendData("testing", "testing", "tvoc", "ppb", float(tvocSensor))
    influxDb.sendData("testing", "testing", "ir", "celsius", float(irSensor))
    influxDb.sendData("testing", "testing", "dht22Temp", "celsius", float(dht22Temp))
    influxDb.sendData("testing", "testing", "dht22Hum", "percent", float(dht22Hum))

    influxDb.sendData("testing", "testing", "irCompensated", "celsius", float(irSensor) + IR_TEMPERATURE_OFFSET_CELSIUS)


#Firebase update job
@tl.job(interval=timedelta(seconds=FIREBASE_INTERVAL))
def firebase():
    if timeRuning > FIREBASE_INTERVAL:
        # if __debug__:
        print ("Firebase job : {}".format(time.ctime()))

        presenceAvg = 0.0
        for i in range(0, 2):
            tempStr, check = influxDb.getAverage(FIREBASE_INTERVAL, 0, "testing", "testing", "presence{p}".format(p = i), "volts")
            presenceAvg += float(tempStr)
            if check == 0:
                return
        presenceAvg = presenceAvg / 3.0 


        moistureAvg, checkMoistureAvg = influxDb.getAverage(FIREBASE_INTERVAL, 0, "testing", "testing", "moisture", "volts")
        tvocAvg, checkTvocAvg = influxDb.getAverage(FIREBASE_INTERVAL, 0, "testing", "testing", "tvoc", "ppb")
        irAvgAll, checkIrAvgAll = influxDb.getAverage(FIREBASE_INTERVAL, 0, "testing", "testing", "irCompensated", "celsius")
        irAvgHighest, checkIrAvgHighest = influxDb.getLast(FIREBASE_INTERVAL, 0, "testing", "testing", "irCompensatedAvgHighest", "celsius")
        str1, str2 = influxDb.getLast(FIREBASE_INTERVAL, 0, "testing", "testing", "presenceCheck", "bool")
        statePresenceLast = bool(str1)
        checkStatePresenceLast = bool(str2)
        str1, str2 = influxDb.getLast(FIREBASE_INTERVAL, 0, "testing", "testing", "moistureCheck", "bool")
        stateMoistureLast = bool(str1)
        checkStateMoistureLast = bool(str2)
        dht22TempAvg, checkDht22TempAvg = influxDb.getAverage(FIREBASE_INTERVAL, 0, "testing", "testing", "dht22Temp", "celsius")
        dht22HumAvg, checkDht22HumAvg = influxDb.getAverage(FIREBASE_INTERVAL, 0, "testing", "testing", "dht22Hum", "percent")
        if ((checkMoistureAvg * checkTvocAvg * checkIrAvgAll * checkIrAvgHighest * checkStatePresenceLast * checkStateMoistureLast * checkDht22TempAvg * checkDht22HumAvg) == 0):
            return
        else:
            fireDb.sendData("presence", presenceAvg)
            fireDb.sendData("moisture", moistureAvg)
            fireDb.sendData("tvoc", tvocAvg)
            fireDb.sendData("ir", irAvgAll)
            fireDb.sendData("irAvgHighest", irAvgHighest)
            fireDb.sendData("presenceState", statePresenceLast)
            fireDb.sendData("moistureState", stateMoistureLast)
            fireDb.sendData("dht22Temp", dht22TempAvg)
            fireDb.sendData("dht22Hum", dht22HumAvg)
    else:
        # if __debug__:
        print ("Firebase job not run timerunning: {time} < Firebase interval: {interval}, job time: {job}".format(time = timeRuning, interval = FIREBASE_INTERVAL, job = time.ctime()))


#Presence sensor detection job: check if there is really presence
@tl.job(interval=timedelta(seconds=PRESENCE_INTERVAL))
def presenceCheck():
    if timeRuning > PRESENCE_INTERVAL:
        # if __debug__:
        print("presenceCheck Job:")
        presence = True
        for i in range(0, 3):   
            avg, check = influxDb.getAverage(PRESENCE_INTERVAL, 0, "testing", "testing", "presence{p}".format(p = i), "volts")
            if check == 0:
                return
            else:
                if avg > PRESENCE_THRESHOLD_V:
                    presence = False

        if __debug__:
            print("presence: {p}".format(p = bool(presence)))

        influxDb.sendData("testing", "testing", "presenceCheck", "bool", bool(presence))
    else:
        # if __debug__:
        print ("presenceCheck job not run timerunning: {time} < presenceCheck interval: {interval}, job time: {job}".format(time = timeRuning, interval = PRESENCE_INTERVAL, job = time.ctime()))

#Moisture sensor detection job: check if there is really moisture
avgDetected = 0.0
@tl.job(interval=timedelta(seconds = MOISTURE_INTERVAL))
def moistureCheck():
    if timeRuning > MOISTURE_INTERVAL * 3:
        # if __debug__:
        print("moistureCheck Job:")
        
        global avgDetected
        avgPast, checkAvgPast = influxDb.getAverage(
            MOISTURE_INTERVAL * 3, MOISTURE_INTERVAL * 2, 
            "testing", "testing", "moisture", "volts")
        
        avgCurrent, checkAvgCurrent = influxDb.getAverage(
            MOISTURE_INTERVAL, 0, 
            "testing", "testing", "moisture", "volts")
        moistureDetected = False
        if ((checkAvgPast * checkAvgCurrent) == 0):
            return
        else:
            if avgCurrent < (avgPast - MOISTURE_FALL_V):
                moistureDetected = True
                avgDetected = avgCurrent

            if avgDetected <= avgCurrent * 1.1 and avgDetected >= avgCurrent * 0.9:
                moistureDetected = True
            else:
                moistureDetected = False
            
            influxDb.sendData("testing", "testing", "moistureCheck", "bool", bool(moistureDetected))

            if __debug__:
                print("mositureDetected?: {m}, avgPast: {aP:.2f}, avgCurrent: {aC:.2f}, avgDetected {aD:.2f} difference: {d:.4f}".format(m = bool(moistureDetected), aP = avgPast, aC = avgCurrent, aD = avgDetected, d = avgPast - avgCurrent))
    else:
        # if __debug__:
        print ("moistureCheck job not run timerunning: {time} < moistureCheck interval: {interval}, job time: {job}".format(time = timeRuning, interval = MOISTURE_INTERVAL, job = time.ctime()))

@tl.job(interval=timedelta(seconds = 1))
def timeRunningIncrement():
    global timeRuning
    timeRuning += 1


#IR sensor get avg of the x% highest compensated IR values
@tl.job(interval=timedelta(seconds = IR_INTERVAL))
def irAvg():
    if timeRuning > IR_INTERVAL:
        # if __debug__:
        print("IR average Job:")
  
        avg, check = influxDb.getAverageOfHighestValues(IR_INTERVAL, 0, "testing", "testing", "irCompensated", "celsius", IR_HIGHEST_PERCENTAGE)
        if check == 0:
            return
        else:
            if __debug__:
                print("temp average of highest values: {t}".format(t = avg))

            influxDb.sendData("testing", "testing", "irCompensatedAvgHighest", "celsius", avg)
    else:
        # if __debug__:
        print ("IR average Job not run timerunning: {time} < IR_INTERVAL: {interval}, job time: {job}".format(time = timeRuning, interval = IR_INTERVAL, job = time.ctime()))



def CheckInternet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False
    
#Main:
while (CheckInternet() == False):
    time.sleep(2)
    print("No internet connection")

print("Internet connected!")

if __name__ == "__main__":
    tl.start(block=True)