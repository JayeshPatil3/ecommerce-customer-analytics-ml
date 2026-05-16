import streamlit as st
import sys
from pathlib import Path

# IMPORT PREDICTION FUNCTION

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from predict import predict_satisfaction


# PAGE CONFIG

st.set_page_config(
    page_title="E-Commerce Customer Satisfaction Predictor",
    page_icon="🛒",
    layout="wide"
)

# TITLE

st.title("🛒 E-Commerce Customer Satisfaction Predictor")

st.markdown("""
Predict whether a customer is likely to be satisfied with their order based on delivery, payment, and product details.
""")


# SIDEBAR INPUTS

st.sidebar.header("Enter Order Details")


order_value = st.sidebar.number_input(
    "Order Value",
    min_value=0.0,
    value=150.0
)

total_items = st.sidebar.number_input(
    "Total Items",
    min_value=1,
    value=1
)

freight_value = st.sidebar.number_input(
    "Freight Value",
    min_value=0.0,
    value=20.0
)

payment_installments = st.sidebar.number_input(
    "Payment Installments",
    min_value=1,
    value=1
)

delivery_days = st.sidebar.number_input(
    "Delivery Days",
    min_value=0,
    value=7
)

delay_days = st.sidebar.number_input(
    "Delay Days",
    value=-3
)

product_weight_g = st.sidebar.number_input(
    "Product Weight (g)",
    min_value=0.0,
    value=500.0
)


# CATEGORY INPUTS

product_category = st.sidebar.selectbox(
    "Product Category",
    [
        "beleza_saude",
        "relogios_presentes",
        "cama_mesa_banho",
        "esporte_lazer",
        "informatica_acessorios",
        "moveis_decoracao",
        "automotivo",
        "utilidades_domesticas"
    ]
)

customer_state = st.sidebar.selectbox(
    "Customer State",
    [
        "SP",
        "RJ",
        "MG",
        "RS",
        "PR",
        "BA",
        "SC"
    ]
)


# PREDICT BUTTON

if st.sidebar.button("Predict Satisfaction"):

    input_data = {
        "order_value": order_value,
        "total_items": total_items,
        "freight_value": freight_value,
        "payment_installments": payment_installments,
        "delivery_days": delivery_days,
        "delay_days": delay_days,
        "product_weight_g": product_weight_g,
        "product_category_name": product_category,
        "customer_state": customer_state
    }

    prediction, probability = predict_satisfaction(input_data)

    st.subheader("Prediction Result")


    if prediction == 1:
        st.success(
            f"✅ Customer is likely SATISFIED\n\nConfidence: {probability:.2%}"
        )
    else:
        st.error(
            f"❌ Customer is likely UNSATISFIED\n\nConfidence: {1 - probability:.2%}"
        )

# BUSINESS INSIGHTS
st.markdown("---")

st.subheader("Key Business Drivers")

st.markdown("""
The model identified these major satisfaction drivers:

- Delivery Delay
- Delivery Speed
- Order Value
- Freight Charges
- Product Weight
- Payment Installments

Customers receiving delayed orders are significantly more likely to leave poor reviews.
""")