from time import sleep

from firebase_admin import credentials, initialize_app, messaging
import influxdb_client

credPath = str('/home/pi/Documents/ISENSIOT-SmartBabyMonitoring/cred.json')
cred = credentials.Certificate(credPath)
initialize_app(cred)

influxdb_bucket = "isensiot"
influxdb_org = "isensiot"
influxdb_token = "aqS3xEhM-DwkuCaAHHKzDzAZXc1bkAlSnQ058gvYzpuSJVRq4rUcdPXAG51t8iQl_q_wMdw3Y5qSwJoCcFOijw=="
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(url=url, token=influxdb_token, org=influxdb_org)
query_api = client.query_api()

items = [
    {"field": "bool", "tag": "moistureCheck", "threshold": False, "title": "Diaper Change Needed!", "body": "Time for a diaper change to keep the little one dry and happy."},
    {"field": "bool", "tag": "isCrying", "threshold": False, "title": "Baby Needs Attention!", "body": "Your baby is crying, let's see what they need - a hug, a snack or a nap?"},
    {"field": "ppb", "tag": "tvoc", "threshold": 400, "title": "Bad Air Quality!", "body": "Let's open up a window and freshen things up."},
    {"field": "celsius", "tag": "irCompensated", "threshold": 36.5, "title": "High Temperature Alert!", "body": "Your baby has a temperature higher than 36.5, time to check in."},
    {"field": "celsius", "tag": "dht22Temp", "threshold": 22, "title": "Room Temperature Alert!", "body": "The room is hotter than 22 degrees, let's cool it down a bit."},
    {"field": "bool", "tag": "presenceCheck", "threshold": False, "title": "Baby Not Present!", "body": "Looks like your baby has left their crib."}
]

def send_notification(tag, title, body):
    try:
        notification = messaging.Notification(
            title= title,
            body= body,
        )
        message = messaging.Message(
            notification=notification,
            topic='high_importance_channel',
        )
        response = messaging.send(message)
        print(f'Notification sent for {tag}: {response}')
    except Exception as e:
        print(f'Error sending notification: {e}')

def getLast(field, tag):
    try:
        query_api = client.query_api()
        query = f'''
                    from(bucket: "{influxdb_bucket}")
                        |> range(start: -1d)
                        |> filter(fn: (r) => r._measurement == "testing")
                        |> filter(fn: (r) => r._field == "{field}")
                        |> filter(fn: (r) => r.testing == "{tag}")
                        |> last()
                '''
        result = query_api.query(org=influxdb_org, query=query)
        for table in result:
            for record in table.records:
                print(record.get_value())
                return record.get_value()
    except Exception as e:
        print(f'Error querying InfluxDB: {e}')
        return None

def getSecondLast(field, tag):
    try:
        query_api = client.query_api()
        query = f'''
                    from(bucket: "{influxdb_bucket}")
                        |> range(start: -1d)
                        |> filter(fn: (r) => r._measurement == "testing")
                        |> filter(fn: (r) => r._field == "{field}")
                        |> filter(fn: (r) => r.testing == "{tag}")
                        |> sort(columns: ["_time"], desc: true)
                        |> limit(n: 2)
                        |> last()
                '''
        result = query_api.query(org=influxdb_org, query=query)
        for table in result:
            for record in table.records:
                print(record.get_value())
                return record.get_value()
    except Exception as e:
        print(f'Error querying InfluxDB: {e}')
        return None

def checkForNotifications():
    for item in items:
        if type(item['threshold']) is bool:
            if bool(getLast(item['field'], item['tag'])) != item['threshold'] and getSecondLast(item['field'], item['tag']) == item['threshold']:
                send_notification(item['tag'], item['title'], item['body'])
        else:
            if getLast(item['field'], item['tag']) > item['threshold'] and getSecondLast(item['field'], item['tag']) <= item['threshold']:
                send_notification(item['tag'], item['title'], item['body'])

def testNotification():
    send_notification(items[0]['tag'], items[0]['title'], items[0]['body'])

while True:
    checkForNotifications()
    sleep(300)
    # testNotification()

