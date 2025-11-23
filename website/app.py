import streamlit as st
from src.web_predict import load_artifacts, predict_from_input

st.set_page_config(page_title="Diabetes Detection", page_icon="🩺")

st.title("🩺 Diabetes Detection Using Machine Learning")
st.write("Enter values to predict whether the patient has diabetes.")

model, scaler, features = load_artifacts()

user_data = {}

cols = st.columns(2)
for i, f in enumerate(features):
    with cols[i % 2]:
        user_data[f] = st.number_input(f, min_value=0.0, step=0.1)

if st.button("Predict Diabetes"):
    values = [user_data[f] for f in features]
    pred, prob = predict_from_input(model, scaler, features, values)

    st.subheader("Prediction Output")

    if pred == 1:
        st.error(f"⚠️ High chance of Diabetes (Probability: {prob:.2f})")
    else:
        st.success(f"✅ No Diabetes Detected (Probability: {prob:.2f})")

    st.progress(prob)
