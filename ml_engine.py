from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

DATA_PATH = Path(__file__).resolve().parent / "data" / "HeartDiseaseTrain-Test.csv"

CAT_COLS = [
    "sex",
    "chest_pain_type",
    "fasting_blood_sugar",
    "rest_ecg",
    "exercise_induced_angina",
    "slope",
    "vessels_colored_by_flourosopy",
    "thalassemia",
]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def train_model(df: pd.DataFrame) -> tuple[RandomForestClassifier, dict[str, LabelEncoder], list[str]]:
    df_model = df.copy()
    encoders: dict[str, LabelEncoder] = {}
    for col in CAT_COLS:
        encoder = LabelEncoder()
        df_model[col] = encoder.fit_transform(df_model[col].astype(str))
        encoders[col] = encoder

    x_train = df_model.drop("target", axis=1)
    y_train = df_model["target"]
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)
    return model, encoders, list(x_train.columns)


def _encode_input(patient_data: dict[str, Any], encoders: dict[str, LabelEncoder]) -> dict[str, Any]:
    encoded = dict(patient_data)
    for col in CAT_COLS:
        value = str(encoded[col])
        encoder = encoders[col]
        encoded[col] = encoder.transform([value])[0] if value in encoder.classes_ else 0
    return encoded


def _risk_bucket(risk_pct: float) -> tuple[str, str]:
    if risk_pct < 30:
        return "Low Risk", "#27AE60"
    if risk_pct < 60:
        return "Moderate Risk", "#F39C12"
    return "High Risk", "#E74C3C"


def predict_risk(
    patient_data: dict[str, Any],
    model: RandomForestClassifier,
    encoders: dict[str, LabelEncoder],
    feature_cols: list[str],
) -> dict[str, Any]:
    encoded = _encode_input(patient_data, encoders)
    inference_df = pd.DataFrame([encoded])[feature_cols]
    risk_prob = float(model.predict_proba(inference_df)[0][1])
    risk_score = round(risk_prob * 100, 1)
    risk_level, risk_color = _risk_bucket(risk_score)
    feature_importance = [
        {"feature": feature, "importance": round(float(importance), 4)}
        for feature, importance in sorted(
            zip(feature_cols, model.feature_importances_), key=lambda item: item[1], reverse=True
        )
    ]
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "feature_importance": feature_importance,
    }


def get_distribution_data(df: pd.DataFrame, sex: str) -> dict[str, dict[str, list[float]]]:
    sex_df = df[df["sex"] == sex]
    healthy_df = sex_df[sex_df["target"] == 0]
    disease_df = sex_df[sex_df["target"] == 1]
    result: dict[str, dict[str, list[float]]] = {}
    for feature in ["resting_blood_pressure", "cholestoral", "Max_heart_rate", "oldpeak"]:
        result[feature] = {
            "healthy": [float(value) for value in healthy_df[feature].dropna().tolist()],
            "disease": [float(value) for value in disease_df[feature].dropna().tolist()],
        }
    return result


DF = load_data()
MODEL, ENCODERS, FEATURE_COLS = train_model(DF)