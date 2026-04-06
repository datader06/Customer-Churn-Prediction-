import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

st.set_page_config(page_title="Customer Churn Predictor", layout="wide")

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"

if not MODEL_PATH.exists():
    st.error(f"Model file not found at: {MODEL_PATH}")
    st.stop()

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

st.title("Customer Churn Prediction System")
st.write("Enter customer details to predict churn probability and get a retention recommendation.")

st.subheader("Customer Input")

gender = st.selectbox("Gender", ["Male", "Female"])
senior = st.selectbox("Senior Citizen", [0, 1])
partner = st.selectbox("Partner", ["Yes", "No"])
dependents = st.selectbox("Dependents", ["Yes", "No"])
tenure = st.slider("Tenure (months)", 0, 72, 12)
phone_service = st.selectbox("Phone Service", ["Yes", "No"])
multiple_lines = st.selectbox("Multiple Lines", ["No phone service", "No", "Yes"])
internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
payment_method = st.selectbox(
    "Payment Method",
    [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]
)
monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=70.0)
total_charges = st.number_input("Total Charges", min_value=0.0, value=1000.0)

if st.button("Predict Churn"):
    input_df = pd.DataFrame([{
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }])

    input_df["charge_per_tenure"] = input_df["TotalCharges"] / (input_df["tenure"] + 1)
    input_df["avg_charge_diff"] = input_df["MonthlyCharges"] - (
        input_df["TotalCharges"] / (input_df["tenure"] + 1)
    )

    services = [
        "PhoneService", "InternetService", "OnlineSecurity", "OnlineBackup",
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"
    ]
    input_df["num_services"] = input_df[services].apply(lambda x: sum(x == "Yes"), axis=1)

    input_df["high_risk"] = (
        (input_df["SeniorCitizen"] == 1) &
        (input_df["Partner"] == "No") &
        (input_df["Dependents"] == "No")
    ).astype(int)

    contract_map = {
        "Month-to-month": 0,
        "One year": 1,
        "Two year": 2
    }
    input_df["contract_type_encoded"] = input_df["Contract"].map(contract_map)

    input_df["tenure_group"] = pd.cut(
        input_df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-1yr", "1-2yr", "2-4yr", "4-6yr"],
        include_lowest=True
    ).astype("object")

    input_df["CLV"] = input_df["MonthlyCharges"] * input_df["tenure"]

    churn_prob = model.predict_proba(input_df)[:, 1][0]
    threshold = 0.3
    prediction = int(churn_prob >= threshold)
    business_score = churn_prob * input_df["CLV"].iloc[0]

    if contract == "Month-to-month":
        action = "Offer long-term contract discount"
    elif monthly_charges > 80:
        action = "Give pricing retention offer"
    elif input_df["num_services"].iloc[0] <= 2:
        action = "Offer bundle upgrade"
    else:
        action = "Retention call by support team"

    st.subheader("Prediction Result")
    st.write(f"**Churn Probability:** {churn_prob:.2%}")
    st.write(
        f"**Predicted Class (threshold=0.3):** "
        f"{'Likely to Churn' if prediction == 1 else 'Not Likely to Churn'}"
    )
    st.write(f"**Estimated CLV:** {input_df['CLV'].iloc[0]:.2f}")
    st.write(f"**Business Score:** {business_score:.2f}")
    st.write(f"**Recommended Action:** {action}")