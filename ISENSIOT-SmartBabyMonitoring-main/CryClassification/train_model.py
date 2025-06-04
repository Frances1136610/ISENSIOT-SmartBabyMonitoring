import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.utils import resample
import pickle
from utils import extract_features

#Train model, it should classify a baby recording in 1 of 6 categories.

#Define path to dataset directory, this script is specific for the donate a cry corpus dataset and has additional audiofiles for background sound
path = '/home/pi/CryClassification/rerecordedDatasetVersionTwo' 

features = []
labels = []

#Loop through all files in dataset and extract features and labels
for label in os.listdir(path):
    print(f"{label} data is loading.....")
    for file_name in os.listdir(os.path.join(path, label)):
        file_path = os.path.join(path, label, file_name)
        feature = extract_features(file_path)
        if feature is not None:
            features.append(feature)
            labels.append(label)
    print(f"{label} data loaded....")

#Make dataframe from labels and features lists to perform oversampling  
df = pd.DataFrame({'label': labels, 'features': features}, columns=['label', 'features'])
#Split dataframe according to labels
df_discomfort = df[df['label'] == 'discomfort']
df_burping = df[df['label'] == 'burping']
df_belly_pain = df[df['label'] == 'belly_pain']
df_tired = df[df['label'] == 'tired']
df_no_cry = df[df['label'] == 'no_cry']
#Keep majority label seperate
df_hungry = df[df['label'] == 'hungry']

#Oversample minority labels to size of majority label, n_samples is the value of df_hungry.shape
df_discomfort_resampled = resample(df_discomfort, random_state=42, n_samples=382, replace=True)
df_burping_resampled = resample(df_burping, random_state=42, n_samples=382, replace=True)
df_belly_pain_resampled = resample(df_belly_pain, random_state=42, n_samples=382, replace=True)
df_tired_resampled = resample(df_tired, random_state=42, n_samples=382, replace=True)
df_no_cry_resampled = resample(df_no_cry, random_state=42, n_samples=382, replace=True)

#Combine dataframes into one
df_1 = pd.concat([df_discomfort_resampled, df_burping_resampled])
df_2 = pd.concat([df_belly_pain_resampled, df_tired_resampled])
df_3 = pd.concat([df_1, df_2])
df_4 = pd.concat([df_3, df_no_cry_resampled])

df_upsampled = pd.concat([df_4, df_hungry])

#Split the resampled dataframe back into lists
features_list = df_upsampled['features'].tolist()
labels_list = df_upsampled['label'].tolist()

#Save features dataframe to csv file for easy retraining
df_upsampled.to_csv('audio_features.csv')

features = np.array(features_list)
labels = np.array(labels_list)

#Split data in 75% train set and 25% test set 
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.25, random_state=42)

#Train model
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

#Test accuracy
#rf_pred = rf.predict(X_test)
#print(rf_pred)
#rf_acc = accuracy_score(y_test, rf_pred)
#print("Random Forest Accuracy:", rf_acc)

filename = 'cry_classifier_model.sav'
pickle.dump(rf, open(filename, 'wb'))
