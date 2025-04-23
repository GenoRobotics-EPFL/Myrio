import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import time
import joblib

# === Step 1: Load and filter dataset ===
df = pd.read_parquet("matK_angiospermae.parquet")
vc = df["species"].value_counts()
valid_species = vc[vc >= 10].index
df_filtered = df[df["species"].isin(valid_species)].copy()

le = LabelEncoder()
df_filtered["label"] = le.fit_transform(df_filtered["species"])

X = df_filtered.drop(columns=["species", "label"])
y = df_filtered["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.5, random_state=42, stratify=y
)

# Convert to DMatrix
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# === Step 2: Define parameters ===
params = {
    "objective": "multi:softmax",
    "num_class": len(le.classes_),
    "eval_metric": "mlogloss",
    "tree_method": "hist",
    "verbosity": 1
}

# === Step 3: Train with early stopping ===
evals_result = {}
print("🚀 Training XGBoost with early stopping...")
start = time.time()
model = xgb.train(
    params,
    dtrain,
    num_boost_round=1000,
    evals=[(dtrain, "train"), (dtest, "test")],
    early_stopping_rounds=20,
    evals_result=evals_result,
    verbose_eval=True
)
end = time.time()
print(f"✅ Training completed in {end - start:.2f} seconds")
print(f"🔁 Best iteration: {model.best_iteration}")

# === Step 4: Predict and evaluate ===
y_pred = model.predict(dtest)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy: {acc:.4f}\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# === Step 5: Save model and label encoder ===
model.save_model("xgb_kmer_model.json")
joblib.dump(le, "species_label_encoder.joblib")

# === Step 6: Plot training log loss ===
epochs = len(evals_result["train"]["mlogloss"])
x_axis = range(epochs)

plt.figure(figsize=(10, 5))
plt.plot(x_axis, evals_result["train"]["mlogloss"], label="Train")
plt.plot(x_axis, evals_result["test"]["mlogloss"], label="Test")
plt.xlabel("Boosting Round")
plt.ylabel("Log Loss")
plt.title("XGBoost Training Progress")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
