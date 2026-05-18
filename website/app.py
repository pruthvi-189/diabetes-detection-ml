import streamlit as st
import numpy as np
import sys
import os

# Allow imports from src/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.web_predict import load_artifacts, predict_from_input

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Diabetes Detection",
    page_icon="🩺",
    layout="centered",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body { font-family: 'Segoe UI', sans-serif; }
    .stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        border: none;
    }
    .stButton > button:hover { background-color: #1D4ED8; }
    .result-box {
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    .positive { background-color: #FEE2E2; color: #991B1B; border-left: 5px solid #EF4444; }
    .negative { background-color: #D1FAE5; color: #065F46; border-left: 5px solid #10B981; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🩺 Diabetes Risk Predictor")
st.markdown("Enter the patient's health metrics below to predict the likelihood of diabetes.")
st.divider()

# ── Load model artifacts ──────────────────────────────────────────────────────
@st.cache_resource
def get_artifacts():
    return load_artifacts()

try:
    model, scaler, features = get_artifacts()
except FileNotFoundError:
    st.error("⚠️ Model not found. Please run `python src/train_model.py` first to train and save the model.")
    st.stop()

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        pregnancies      = st.number_input("Pregnancies",           min_value=0,   max_value=20,   value=1,   step=1)
        glucose          = st.number_input("Glucose (mg/dL)",       min_value=0,   max_value=300,  value=110, step=1)
        blood_pressure   = st.number_input("Blood Pressure (mmHg)", min_value=0,   max_value=200,  value=72,  step=1)
        skin_thickness   = st.number_input("Skin Thickness (mm)",   min_value=0,   max_value=100,  value=20,  step=1)

    with col2:
        insulin          = st.number_input("Insulin (μU/mL)",       min_value=0,   max_value=900,  value=79,  step=1)
        bmi              = st.number_input("BMI",                   min_value=0.0, max_value=70.0, value=25.0, step=0.1, format="%.1f")
        dpf              = st.number_input("Diabetes Pedigree Fn",  min_value=0.0, max_value=3.0,  value=0.5, step=0.01, format="%.2f")
        age              = st.number_input("Age",                   min_value=1,   max_value=120,  value=33,  step=1)

    submitted = st.form_submit_button("🔍 Predict", use_container_width=True)

# ── Prediction result ─────────────────────────────────────────────────────────
if submitted:
    input_values = [pregnancies, glucose, blood_pressure, skin_thickness,
                    insulin, bmi, dpf, age]

    prediction, probability = predict_from_input(model, scaler, features, input_values)

    st.divider()
    if prediction == 1:
        st.markdown(
            f'<div class="result-box positive">⚠️ High Risk of Diabetes &nbsp;|&nbsp; Confidence: {probability * 100:.1f}%</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="result-box negative">✅ Low Risk of Diabetes &nbsp;|&nbsp; Confidence: {(1 - probability) * 100:.1f}%</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("⚕️ This tool is for educational purposes only and should not replace professional medical advice.")
