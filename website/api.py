# -*- coding: utf-8 -*-
"""
Flask REST API for Diabetes Detection ML Model
"""

import os
import sys
import json
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Allow imports from src/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.web_predict import load_artifacts, predict_from_input

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# Load artifacts once at startup
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

try:
    # Change working directory context for model loading
    original_dir = os.getcwd()
    os.chdir(BASE_DIR)
    model, scaler, features = load_artifacts()
    os.chdir(original_dir)
    print("[OK] Model loaded successfully.")
    print(f"   Features: {features}")
except Exception as e:
    print(f"[ERROR] Error loading model: {e}")
    model, scaler, features = None, None, None


@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Run src/train_model.py first."}), 503

    try:
        data = request.get_json(force=True)

        # Extract features in order
        feature_order = [
            "pregnancies", "glucose", "blood_pressure", "skin_thickness",
            "insulin", "bmi", "dpf", "age"
        ]

        input_values = []
        for key in feature_order:
            val = data.get(key)
            if val is None:
                return jsonify({"error": f"Missing field: {key}"}), 400
            input_values.append(float(val))

        prediction, probability = predict_from_input(model, scaler, features, input_values)

        return jsonify({
            "prediction": int(prediction),
            "probability": float(probability),
            "risk_level": get_risk_level(probability),
            "confidence": float(probability) if prediction == 1 else float(1 - probability),
            "features_used": features,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "features": features if features else []
    })


def get_risk_level(probability):
    if probability < 0.3:
        return "Low"
    elif probability < 0.6:
        return "Moderate"
    elif probability < 0.8:
        return "High"
    else:
        return "Very High"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
