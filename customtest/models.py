import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

# === Step 1: Load dataset ===
df = pd.read_parquet("matK_kmer_cleaned.parquet")

# === Step 2: Filter out rare species (fewer than 2 samples) ===
vc = df["species"].value_counts()
valid_species = vc[vc >= 100].index
df_filtered = df[df["species"].isin(valid_species)].copy()  # make copy to avoid SettingWithCopyWarning

# === Step 3: Label encode species column ===
le = LabelEncoder()
df_filtered["label"] = le.fit_transform(df_filtered["species"])

# === Step 4: Prepare features and labels ===
X = df_filtered.drop(columns=["species", "label"])
y = df_filtered["label"]

# === Step 5: Train-test split with stratification on species ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.5, random_state=42, stratify=y  # stratify to preserve class balance
)

# === Step 6: Train XGBoost model ===
model = xgb.XGBClassifier(
    objective="multi:softmax",
    num_class=len(le.classes_),
    eval_metric="mlogloss",
    n_jobs=-1,
    tree_method="hist",
    verbosity=1
)
print("Training XGBoost model...")
model.fit(X_train, y_train, verbose=True)

# === Step 7: Predict and evaluate ===
print("Predicting on test set...")
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy: {acc:.4f}\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# === Step 8: Save model and encoder ===
joblib.dump(model, "xgb_kmer_model.joblib")
joblib.dump(le, "species_label_encoder.joblib")
