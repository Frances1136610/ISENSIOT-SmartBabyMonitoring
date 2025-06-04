import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta

class FirebaseSender():
    db = []
    
    def setupConnection(self, credPath):
        # Use the application.
        cred = credentials.Certificate(str(credPath))
        app = firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def sendData(self, name, value):
        timezone_offset = +2.0  # UTC +2
        tzinfo = timezone(timedelta(hours=timezone_offset))
        time = datetime.now(tzinfo)

        data = {"value": value, "timestamp" : time}
        self.db.collection(name).add(data)

    def sendDataEmotion(self, name, value1, value2):
        timezone_offset = +2.0  # UTC +2
        tzinfo = timezone(timedelta(hours=timezone_offset))
        time = datetime.now(tzinfo)

        data = {"emotion": value1, "isCrying": value2, "timestamp" : time}
        self.db.collection(name).add(data)

    def getEmotionState(self, key):
        doc_ref =  self.db.collection('babyEmotion')
        try:
            docs = doc_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).get()
            for doc in docs:
                return doc.to_dict().get(key)
        except:
            print("No documents found")
    