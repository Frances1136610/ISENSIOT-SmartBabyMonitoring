import pickle
import pandas as pd
from utils import *


#Load pre-trained model
cry_classifier_model_path = 'cry_classifier_model.sav'
cry_classifier_model = pickle.load(open(cry_classifier_model_path, 'rb'))

baby_recording_path = 'baby_recording.wav'
normalized_audio_path = 'normalized_audio.wav'

while True:

	#Record 7 seconds of baby's room sounds, method saves recording as wav-file to baby_recording_path
	record_baby_sound()

	#Extract features from baby recording
	features = extract_features(baby_recording_path)
	#Save features as a datafame
	df_feats = pd.DataFrame(features).transpose()

	prediction = cry_classifier_model.predict(df_feats)
	print(prediction[0])

	isCrying = None
	if prediction[0] != "no_cry":
		isCrying = False
	else:
		isCrying = True

	print("state:")
	print (isCrying)

	# influxDb.sendData("testing", "testing", "isCrying", "bool", isCrying)

	# Check if prediction differs from latest value in database, save prediction to database only then
	if prediction != 'no_cry':
		if fireDb.getEmotionState('isCrying'):
			if fireDb.getEmotionState('emotion') != prediction[0]:
				send_to_firestore(str(prediction[0]), True)
		else:
			send_to_firestore(str(prediction[0]), True)
	else:
		if fireDb.getEmotionState('isCrying'):
			send_to_firestore("Happy", False)


