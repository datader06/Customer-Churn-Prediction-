# Customer Churn Prediction System

This project predicts customer churn for a subscription-based business using machine learning and adds a business layer to prioritize which customers should be targeted for retention.

## Project Overview

The system uses customer demographic, service, billing, and contract information to predict churn probability. It also combines churn risk with customer lifetime value (CLV) to rank customers by business impact.

## Features

- Data cleaning and EDA
- Feature engineering
- Preprocessing pipeline with ColumnTransformer
- Model comparison using Logistic Regression, Random Forest, and XGBoost
- Threshold tuning for business-focused recall
- Business layer using churn probability × CLV
- SHAP explainability
- Streamlit app for user interaction

## Dataset

IBM Telco Customer Churn Dataset from Kaggle.

## Model Selection

Logistic Regression was selected because it gave the best recall and ROC-AUC for this churn prediction problem.

## Business Value

Instead of just predicting churn, the project identifies the top customers to target based on:
- churn probability
- customer lifetime value
- recommended retention action

## How to Run

```bash
pip install -r requirements.txt
python -m streamlit run app/app.py