import joblib
import numpy as np
import os

model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
features_path = os.path.join(os.path.dirname(__file__), 'features.pkl')

model = joblib.load(model_path)
features = joblib.load(features_path)

def predict_consumption(hour, day_of_week, month, voltage, sub_metering_1, sub_metering_2, sub_metering_3):
    input_data = np.array([[hour, day_of_week, month, voltage, sub_metering_1, sub_metering_2, sub_metering_3]])
    prediction = model.predict(input_data)
    return round(float(prediction[0]), 4)