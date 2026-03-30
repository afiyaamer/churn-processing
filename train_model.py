import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# ── Load dataset ──────────────────────────────────────────────────────────────
df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")
df = df.drop("customerID", axis=1)

# ── Fix TotalCharges ──────────────────────────────────────────────────────────
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)

# ── Engineer high-signal features ─────────────────────────────────────────────
addon_cols = ["OnlineSecurity", "OnlineBackup", "DeviceProtection",
              "TechSupport", "StreamingTV", "StreamingMovies"]

# Replace Yes/No before engineering
df = df.replace({"Yes": 1, "No": 0})

# Count how many add-on services the customer has (0–6)
df["NumAddonServices"] = df[addon_cols].sum(axis=1)

# ── Select final feature set ───────────────────────────────────────────────────
# These are the highest-signal features based on telecom churn research
SELECTED_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "SeniorCitizen",
    "PaperlessBilling",
    "NumAddonServices",
    "TechSupport",
    "OnlineSecurity",
    # Categorical → will be one-hot encoded
    "Contract",
    "InternetService",
    "PaymentMethod",
]

df_model = df[SELECTED_FEATURES + ["Churn"]].copy()
df_model["Churn"] = df_model["Churn"].replace({"Yes": 1, "No": 0})

# ── One-hot encode categorical columns ────────────────────────────────────────
df_model = pd.get_dummies(df_model, columns=["Contract", "InternetService", "PaymentMethod"])

# ── Split features / target ───────────────────────────────────────────────────
X = df_model.drop("Churn", axis=1)
y = df_model["Churn"]

# Save column names for app.py to use
joblib.dump(X.columns.tolist(), "columns.pkl")
print(f"✅ Saved {len(X.columns)} feature columns: {X.columns.tolist()}")

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Scale ─────────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
joblib.dump(scaler, "scaler.pkl")

# ── Train model ───────────────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=5,
    class_weight="balanced",   # handles class imbalance (~26% churn)
    random_state=42,
    n_jobs=-1
)
model.fit(X_train_scaled, y_train)
joblib.dump(model, "churn_model.pkl")

# ── Evaluate ──────────────────────────────────────────────────────────────────
print("\n📊 Test Set Performance:")
print(classification_report(y_test, model.predict(X_test_scaled),
                             target_names=["Stay", "Churn"]))
print("✅ Model, scaler, and columns saved successfully!")
