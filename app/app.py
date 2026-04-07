"""
Customer Churn Prediction System - Streamlit Application

This module provides an interactive web interface for predicting customer churn
and recommending retention actions based on churn probability and customer lifetime value.

Author: Data Science Team
Version: 1.0.0
"""

import logging
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from typing import Tuple, Dict, Any
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
CHURN_THRESHOLD = 0.3
TENURE_BINS = [0, 12, 24, 48, 72]
TENURE_LABELS = ["0-1yr", "1-2yr", "2-4yr", "4-6yr"]
HIGH_MONTHLY_CHARGE = 80.0
MIN_SERVICES_FOR_BUNDLE = 2

# Page configuration
st.set_page_config(
    page_title="Customer Churn Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"

def check_model_exists() -> bool:
    """
    Check if the model file exists at the expected location.
    
    Returns:
        bool: True if model exists, False otherwise
    """
    if not MODEL_PATH.exists():
        logger.error(f"Model file not found at: {MODEL_PATH}")
        return False
    logger.info(f"Model file found at: {MODEL_PATH}")
    return True

@st.cache_resource
def load_model():
    """
    Load the trained model from disk with caching.
    
    Returns:
        Trained model object
        
    Raises:
        FileNotFoundError: If model file doesn't exist
    """
    try:
        logger.info("Loading model from disk...")
        model = joblib.load(MODEL_PATH)
        logger.info("Model loaded successfully")
        return model
    except FileNotFoundError as e:
        logger.error(f"Failed to load model: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading model: {e}")
        raise

# Validate model exists before loading
if not check_model_exists():
    st.error(f"❌ Model file not found at: {MODEL_PATH}\n\nPlease ensure the model has been trained and saved.")
    st.stop()

try:
    model = load_model()
except Exception as e:
    st.error(f"❌ Failed to load model: {str(e)}")
    logger.exception("Model loading failed")
    st.stop()

st.title("🔮 Customer Churn Prediction System")
st.markdown("""
Enter customer details to predict churn probability and get a personalized retention recommendation.
""")

# Sidebar for information
with st.sidebar:
    st.header("ℹ️ How It Works")
    st.markdown("""
    **This system:**
    1. Analyzes customer characteristics
    2. Predicts churn probability
    3. Calculates customer lifetime value
    4. Recommends targeted retention actions
    
    **Churn Threshold:** 30% (customers with >30% churn risk are flagged)
    """)

col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Demographics")
    gender = st.selectbox("Gender", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])

with col2:
    st.subheader("📊 Account Information")
    tenure = st.slider("Tenure (months)", min_value=0, max_value=72, value=12, step=1)
    monthly_charges = st.number_input("Monthly Charges ($)", min_value=0.0, value=70.0, step=0.01)
    total_charges = st.number_input("Total Charges ($)", min_value=0.0, value=1000.0, step=0.01)

col3, col4 = st.columns(2)

with col3:
    st.subheader("📞 Services")
    phone_service = st.selectbox("Phone Service", ["Yes", "No"], key="phone")
    multiple_lines = st.selectbox("Multiple Lines", ["No phone service", "No", "Yes"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])

with col4:
    st.subheader("🔧 Subscriptions")
    online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
    online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
    device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
    tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
    streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
    streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])

col5, col6 = st.columns(2)

with col5:
    st.subheader("💳 Billing")
    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])

with col6:
    st.subheader("💰 Payment")
    payment_method = st.selectbox(
        "Payment Method",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ]
    )

def validate_input_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate input data for anomalies and constraints.
    
    Args:
        data: Dictionary containing input features
        
    Returns:
        Tuple of (is_valid, message)
    """
    if data["tenure"] == 0 and data["total_charges"] > 0:
        return False, "⚠️ Warning: Tenure is 0 months but total charges > 0"
    
    if data["tenure"] > 0 and data["total_charges"] == 0:
        return False, "⚠️ Warning: Tenure > 0 but total charges = 0"
    
    if data["monthly_charges"] > 500:
        return False, "⚠️ Warning: Monthly charges exceed reasonable limits (>$500)"
    
    return True, ""

def create_input_dataframe(
    gender: str, senior: int, partner: str, dependents: str,
    tenure: int, phone_service: str, multiple_lines: str,
    internet_service: str, online_security: str, online_backup: str,
    device_protection: str, tech_support: str, streaming_tv: str,
    streaming_movies: str, contract: str, paperless_billing: str,
    payment_method: str, monthly_charges: float, total_charges: float
) -> pd.DataFrame:
    """
    Create and validate input dataframe with feature engineering.
    
    Returns:
        pd.DataFrame: Processed input data
    """
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

    # Feature engineering
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
        bins=TENURE_BINS,
        labels=TENURE_LABELS,
        include_lowest=True
    ).astype("object")

    input_df["CLV"] = input_df["MonthlyCharges"] * input_df["tenure"]

    return input_df

def get_retention_action(
    contract: str,
    monthly_charges: float,
    num_services: int,
    churn_prob: float
) -> str:
    """
    Determine the recommended retention action based on customer profile.
    
    Args:
        contract: Type of contract
        monthly_charges: Monthly charge amount
        num_services: Number of services subscribed
        churn_prob: Predicted churn probability
        
    Returns:
        str: Recommended action
    """
    if churn_prob < 0.15:
        return "✅ No action needed - Low churn risk"
    elif contract == "Month-to-month":
        return "📋 Offer 12-month contract discount to increase commitment"
    elif monthly_charges > HIGH_MONTHLY_CHARGE:
        return "💰 Launch pricing retention offer & loyalty discount"
    elif num_services <= MIN_SERVICES_FOR_BUNDLE:
        return "📦 Recommend service bundle upgrade to increase engagement"
    else:
        return "📞 Assign to proactive retention specialist for personal outreach"

# Prediction button
if st.button("🚀 Predict Churn", use_container_width=True, type="primary"):
    try:
        # Validate input
        is_valid, warning_msg = validate_input_data({
            "tenure": tenure,
            "total_charges": total_charges,
            "monthly_charges": monthly_charges
        })
        
        if not is_valid:
            st.warning(warning_msg)
        
        logger.info("Creating input dataframe...")
        
        # Create input dataframe
        input_df = create_input_dataframe(
            gender, senior, partner, dependents, tenure, phone_service,
            multiple_lines, internet_service, online_security, online_backup,
            device_protection, tech_support, streaming_tv, streaming_movies,
            contract, paperless_billing, payment_method, monthly_charges,
            total_charges
        )

        logger.info("Making prediction...")
        
        # Get predictions
        churn_prob = model.predict_proba(input_df)[:, 1][0]
        prediction = int(churn_prob >= CHURN_THRESHOLD)
        business_score = churn_prob * input_df["CLV"].iloc[0]
        num_services = input_df["num_services"].iloc[0]
        
        # Determine action
        action = get_retention_action(contract, monthly_charges, num_services, churn_prob)
        
        logger.info(f"Prediction completed - Churn Prob: {churn_prob:.2%}")

        # Display results
        st.success("✅ Prediction Complete!")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Churn Probability", f"{churn_prob:.1%}")
        
        with col2:
            st.metric("Churn Risk", "🔴 High" if prediction == 1 else "🟢 Low")
        
        with col3:
            st.metric("Customer Lifetime Value", f"${input_df['CLV'].iloc[0]:.2f}")
        
        with col4:
            st.metric("Business Risk Score", f"${business_score:.2f}")

        st.divider()
        
        st.subheader("🎯 Recommended Action")
        st.info(action)
        
        # Additional insights
        with st.expander("📊 Detailed Metrics"):
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.write(f"**Tenure:** {tenure} months")
                st.write(f"**Monthly Charge:** ${monthly_charges:.2f}")
            with metrics_col2:
                st.write(f"**Total Charge:** ${total_charges:.2f}")
                st.write(f"**Services:** {num_services}/8")
            with metrics_col3:
                st.write(f"**Contract:** {contract}")
                st.write(f"**High Risk Group:** {'Yes' if input_df['high_risk'].iloc[0] == 1 else 'No'}")
        
    except Exception as e:
        logger.exception("Error during prediction")
        st.error(f"❌ Prediction failed: {str(e)}")
        st.info("Please check your inputs and try again. If the problem persists, contact support.")