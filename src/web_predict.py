import os
import joblib
import numpy as np


def load_artifacts():
    model = joblib.load("models/diabetes_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    features = joblib.load("models/feature_names.pkl")
    return model, scaler, features


def predict_from_input(model, scaler, features, input_values):
    arr = np.array(input_values).reshape(1, -1)
    arr_scaled = scaler.transform(arr)
    pred = model.predict(arr_scaled)[0]
    prob = model.predict_proba(arr_scaled)[0][1]
    return pred, prob
