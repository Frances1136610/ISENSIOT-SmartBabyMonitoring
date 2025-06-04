import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import random
import time


class InfluxSender():
    client = []
    write_api = []
    bucket = []
    org = []
   
    def setupConnection(self, bucket, org, token, url):
        self.client = influxdb_client.InfluxDBClient(
            url=url,
            token=token,
            org=org
        )
        self.bucket = bucket
        self.org = org
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def sendData(self, measurement, tag1, tag2, fieldName, fieldData):
        p = influxdb_client.Point(str(measurement)).tag(str(tag1), str(tag2)).field(str(fieldName), fieldData)
        self.write_api.write(bucket=self.bucket, org=self.org, record=p)
        if __debug__:
            print(p)

    def getAverage(self, timeStart, timeEnd, measurement, tag1, tag2, fieldName):
        if __debug__:
            print("get average")

        query_api = self.client.query_api()
        query = 'from(bucket: "isensiot")\
                |> range(start: {tStart}, stop: {tEnd})\
                |> filter(fn: (r) => r["_measurement"] == "{meas}")\
                |> filter(fn: (r) => r["_field"] == "{field}")\
                |> filter(fn: (r) => r["testing"] == "{tag}")\
                |> aggregateWindow(every: 15m, fn: mean, createEmpty: false)\
                |> group()\
                |> mean()\
                |> yield(name: "mean")'.format(tStart = ("-" + str(timeStart) + 's'), tEnd = ("-" + str(timeEnd) + 's'), meas = str(measurement), field = str(fieldName), tag = str(tag2))
        if __debug__:
            print(query)

        result = query_api.query(org=self.org, query=query)
        results = []
        empty = True
        for table in result:
            for record in table.records:
                results.append((record.get_value()))
                empty = False

        if empty == True:
            if __debug__:
                print("Not enough values to get average, skipping")
                
            return 0, 0
        else:
            if __debug__:
                print(float(results[0]))

            return float(results[0]), 1
    
    def getLast(self, timeStart, timeEnd, measurement, tag1, tag2, fieldName):
        if __debug__:
            print("get last")
        
        query_api = self.client.query_api()
        query ='from(bucket: "isensiot")\
            |> range(start: {tStart}, stop: {tEnd})\
            |> filter(fn: (r) => r["_measurement"] == "{meas}")\
            |> filter(fn: (r) => r["_field"] == "{field}")\
            |> filter(fn: (r) => r["testing"] == "{tag}")\
            |> last()\
            |> yield()'.format(tStart = ("-" + str(timeStart) + 's'), tEnd = ("-" + str(timeEnd) + 's'), meas = str(measurement), field = str(fieldName), tag = str(tag2))
            
        if __debug__:
            print(query)

        result = query_api.query(org=self.org, query=query)
        results = []
        empty = True
        for table in result:
            for record in table.records:
                results.append((record.get_value()))
                empty = False

        if empty == True:
            if __debug__:
                print("Not enough values to get average, skipping")
                
            return 0, 0
        else:
            if __debug__:
                print(float(results[0]))

            return float(results[0]), 1
    
    def getAverageOfHighestValues(self, timeStart, timeEnd, measurement, tag1, tag2, fieldName, percent):
        if __debug__:
            print("get average of highest values")

        #Get max value
        query_api = self.client.query_api()
        query = 'from(bucket: "isensiot")\
            |> range(start: {tStart}, stop: {tEnd})\
            |> filter(fn: (r) => r["_measurement"] == "{meas}")\
            |> filter(fn: (r) => r["_field"] == "{field}")\
            |> filter(fn: (r) => r["testing"] == "{tag}")\
            |> max()\
            |> yield()'.format(tStart = ("-" + str(timeStart) + 's'), tEnd = ("-" + str(timeEnd) + 's'), meas = str(measurement), field = str(fieldName), tag = str(tag2), percentage = percent / 100)
        if __debug__:
            print(query)

        result = query_api.query(org=self.org, query=query)
        results = []
        empty = True
        for table in result:
            for record in table.records:
                results.append((record.get_value()))
                empty = False
        if empty == True:
            if __debug__:
                print("Not enough values to get average, skipping")
                
            return 0, 0
        else: 
            maxValue = float(results[0])
            if __debug__:
                print("Max value: " + str(maxValue))

            xPercentage = maxValue * (percent / 100)
            if __debug__:
                print("Percentage of max value: " + str(xPercentage))
            
            threshold = maxValue - xPercentage
            if __debug__:
                print("Threshold based on percentage: " + str(percent) + "%, is: " + str(threshold))

            #Get all values above threshold and take average
            query_api = self.client.query_api()
            query = 'from(bucket: "isensiot")\
                |> range(start: {tStart}, stop: {tEnd})\
                |> filter(fn: (r) => r["_measurement"] == "{meas}")\
                |> filter(fn: (r) => r["_field"] == "{field}")\
                |> filter(fn: (r) => r["testing"] == "{tag}")\
                |> filter(fn: (r) => r._value >= {th})  // Filter values above threshold\
                |> mean(column: "_value")  \
                |> yield()'.format(tStart = ("-" + str(timeStart) + 's'), tEnd = ("-" + str(timeEnd) + 's'), meas = str(measurement), field = str(fieldName), tag = str(tag2), th = threshold)
            if __debug__:
                print(query)

            result = query_api.query(org=self.org, query=query)
            results = []
            empty2 = False
            for table in result:
                for record in table.records:
                    results.append((record.get_value()))
                    empty2 = True
            if empty == True:
                if __debug__:
                    print("Not enough values to get average, skipping")
    
                return 0, 0
            else: 
                averageOfHighestValues = float(results[0])

                return averageOfHighestValues, 1
