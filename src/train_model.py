import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

from config import RAW_DATA, PROCESSED_DATA, MODELS


# =========================
# LOAD DATA
# =========================

orders = pd.read_csv(RAW_DATA / "olist_orders_dataset.csv")
customers = pd.read_csv(RAW_DATA / "olist_customers_dataset.csv")
items = pd.read_csv(RAW_DATA / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_DATA / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW_DATA / "olist_order_reviews_dataset.csv")
products = pd.read_csv(RAW_DATA / "olist_products_dataset.csv")


# =========================
# CLEAN PAYMENTS
# =========================

payments_clean = payments.groupby("order_id", as_index=False).agg({
    "payment_value": "sum",
    "payment_installments": "max"
})


# =========================
# MERGE MAIN TABLES
# =========================

df = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(payments_clean, on="order_id", how="left")
)


# =========================
# CONVERT DATE COLUMNS
# =========================

date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for col in date_cols:
    df[col] = pd.to_datetime(df[col])


# =========================
# MERGE ITEMS & PRODUCTS
# =========================

df_items = (
    df
    .merge(items, on="order_id", how="left")
    .merge(products, on="product_id", how="left")
)


# =========================
# FEATURE ENGINEERING
# =========================

df_items["delivery_days"] = (
    df_items["order_delivered_customer_date"]
    - df_items["order_purchase_timestamp"]
).dt.days

df_items["delay_days"] = (
    df_items["order_delivered_customer_date"]
    - df_items["order_estimated_delivery_date"]
).dt.days

df_items["order_value"] = (
    df_items.groupby("order_id")["price"]
    .transform("sum")
)

df_items["total_items"] = (
    df_items.groupby("order_id")["order_item_id"]
    .transform("count")
)


# =========================
# MERGE REVIEWS
# =========================

df_items = df_items.merge(reviews, on="order_id", how="left")


# =========================
# SAVE MASTER DATASET
# =========================

df_items.to_csv(
    PROCESSED_DATA / "ecommerce_master.csv",
    index=False
)


# =========================
# CREATE ML DATASET
# =========================

df_ml = df_items.copy()

df_ml["satisfaction_label"] = df_ml["review_score"].apply(
    lambda x: 1 if x >= 4 else 0
)


# =========================
# SELECT FEATURES
# =========================

features = [
    "order_value",
    "total_items",
    "freight_value",
    "payment_installments",
    "delivery_days",
    "delay_days",
    "product_category_name",
    "customer_state",
    "product_weight_g"
]

df_model = df_ml[features + ["satisfaction_label"]].copy()


# =========================
# HANDLE MISSING VALUES
# =========================

num_cols = [
    "order_value",
    "total_items",
    "freight_value",
    "payment_installments",
    "delivery_days",
    "delay_days",
    "product_weight_g"
]

for col in num_cols:
    df_model[col] = df_model[col].fillna(
        df_model[col].median()
    )

cat_cols = [
    "product_category_name",
    "customer_state"
]

for col in cat_cols:
    df_model[col] = df_model[col].fillna("Unknown")


# =========================
# ONE HOT ENCODING
# =========================

df_model = pd.get_dummies(
    df_model,
    columns=["product_category_name", "customer_state"],
    drop_first=True
)


# =========================
# SPLIT DATA
# =========================

X = df_model.drop("satisfaction_label", axis=1)
y = df_model["satisfaction_label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================
# TRAIN MODEL
# =========================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# =========================
# EVALUATION
# =========================

y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))


# =========================
# FEATURE IMPORTANCE
# =========================

feature_importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="Importance",
    ascending=False
)

print("\nTop 15 Important Features:\n")
print(feature_importance.head(15))


# =========================
# SAVE MODEL
# =========================

joblib.dump(
    model,
    MODELS / "customer_satisfaction_model.pkl"
)

joblib.dump(
    X.columns.tolist(),
    MODELS / "model_features.pkl"
)

print("\nModel and feature list saved successfully.")