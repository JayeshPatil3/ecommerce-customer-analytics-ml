import pandas as pd
import joblib

from config import MODELS


# =========================
# LOAD MODEL
# =========================

model = joblib.load(
    MODELS / "customer_satisfaction_model.pkl"
)

model_features = joblib.load(
    MODELS / "model_features.pkl"
)


# =========================
# PREDICTION FUNCTION
# =========================

def predict_satisfaction(input_data):

    input_df = pd.DataFrame([input_data])

    input_df = pd.get_dummies(input_df)

    input_df = input_df.reindex(
        columns=model_features,
        fill_value=0
    )

    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(input_df)[0][1]

    return prediction, probability