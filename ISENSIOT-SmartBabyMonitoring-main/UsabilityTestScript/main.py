import datetime
import time
import firebase_admin
from firebase_admin import credentials, firestore, messaging

cred = credentials.Certificate("isensiot-b9d43-firebase-adminsdk-qajgx-5e02470718.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'isensiot-b9d43.appspot.com'
})

db = firestore.client()

def send_notification(title, body):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic='high_importance_channel',
        )
        response = messaging.send(message)
        print(f'Notification sent: {response}')
    except Exception as e:
        print(f'Error sending notification: {e}')

#Reset all states
presence_col_ref = db.collection('presenceState')
presence_col_ref.add({'timestamp': datetime.datetime.now(), 'value': False})
moisture_col_ref = db.collection('moistureState')
moisture_col_ref.add({'timestamp': datetime.datetime.now(), 'value': False})
crying_col_ref = db.collection('babyEmotion')
crying_col_ref.add({'timestamp': datetime.datetime.now(), 'isCrying': False, 'emotion': 'happy'})
temperature_col_ref = db.collection('dht22Temp')
temperature_col_ref.add({'timestamp': datetime.datetime.now(), 'value': 19})
ir_col_ref = db.collection('ir')
ir_col_ref.add({'timestamp': datetime.datetime.now(), 'value': 37})
doc_ref = db.collection('sound').document('playSound')
doc_ref.set({"playSound": False})

#baby has been put in crib
time.sleep(5)
presence_col_ref = db.collection('presenceState')
presence_col_ref.add({'timestamp': datetime.datetime.now(), 'value': True})
print("baby has been put in crib")
send_notification('Baby has been put in bed', "It seems that the baby is put in bed, sleep tight!")

#baby pees in bed
time.sleep(3)
moisture_col_ref = db.collection('moistureState')
moisture_col_ref.add({'timestamp': datetime.datetime.now(), 'value': True})
print("baby pees in bed")
send_notification('Diaper Change Needed!', 'The baby has peed. Time for a diaper change to keep them dry and happy')

#baby starts crying
time.sleep(5)
crying_col_ref = db.collection('babyEmotion')
crying_col_ref.add({'timestamp': datetime.datetime.now(), 'isCrying': True, 'emotion': 'uncomfortable'})
print("baby starts crying")
send_notification('Baby Needs Attention!', "The baby is crying. Let's see what they need - a hug, a snack, or a nap?")

#check if talks to baby
print("check if talks to baby")
sound_doc_ref = db.collection('sound').document('playSound')
last_cryData = crying_col_ref.order_by('timestamp', direction='DESCENDING').limit(1).get()[0]
while last_cryData.to_dict()['isCrying']:
    # print(last_cryData.to_dict())
    last_cryData = crying_col_ref.order_by('timestamp', direction='DESCENDING').limit(1).get()[0]
    if sound_doc_ref.get().to_dict()['playSound']:
        crying_col_ref.add({'timestamp': datetime.datetime.now(), 'isCrying': False, 'emotion': 'uncomfortable'})
        print("Parent talked to baby, baby is still uncomfortable because of wet bed but it stopped crying ")

time.sleep(30)

#room temp increases
print("room temp increases")
temperature_col_ref = db.collection('dht22Temp')
temperature_col_ref.add({'timestamp': datetime.datetime.now(), 'value': 25})
time.sleep(30)
send_notification('Room Temperature Alert!', "The baby room is over 22 degrees. Let's cool it down a bit.")

#body temperature increases
print("body temperature increases")
ir_col_ref = db.collection('ir')
ir_col_ref.add({'timestamp': datetime.datetime.now(), 'value': 38.2})
time.sleep(30)
send_notification('High Temperature Alert!', "The baby's body temperature is a too high. Time to check in.")

#baby climbs out of crib
print("baby climbs out of crib")
presence_col_ref = db.collection('presenceState')
presence_col_ref.add({'timestamp': datetime.datetime.now(), 'value': False})
send_notification('Baby has Escaped!', "It seems the baby has left the crib. Maybe time to see what they're up to!")