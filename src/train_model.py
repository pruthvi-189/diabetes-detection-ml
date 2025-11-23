import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib


def load_data(csv_path="data/diabetes.csv"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset missing at {csv_path}")
    return pd.read_csv(csv_path)


def preprocess_data(df):
    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, list(X.columns)


def train_model(X_train, y_train):
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model


def save_artifacts(model, scaler, features):
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/diabetes_model.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(features, "models/feature_names.pkl")
    print("Model and scaler saved successfully!")


def main():
    df = load_data()
    X_train, X_test, y_train, y_test, scaler, features = preprocess_data(df)
    model = train_model(X_train, y_train)

    preds = model.predict(X_test)
    print("\nAccuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))

    save_artifacts(model, scaler, features)


if __name__ == "__main__":
    main()
