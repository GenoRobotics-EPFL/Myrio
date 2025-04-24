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
df = pd.read_parquet("ITS.parquet")
vc = df["genus"].value_counts()
valid_species = vc[vc >= 110].index
df_filtered = df[df["genus"].isin(valid_species)].copy()
print("Vailid genus count:", len(valid_species))
le = LabelEncoder()
df_filtered["label"] = le.fit_transform(df_filtered["genus"])

X = df_filtered.drop(columns=["genus", "label"])
y = df_filtered["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.8, random_state=42, stratify=y
)

# Convert to DMatrix
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# === Step 2: Define parameters ===
params = {
    "objective": "multi:softmax",
    "num_class": len(le.classes_),
    "eval_metric": "mlogloss",
    "tree_method": "gpu_hist",
    "verbosity": 1
}

# === Step 3: Train with early stopping ===
evals_result = {}
print("🚀 Training XGBoost with early stopping...")
start = time.time()
model = xgb.train(
    params,
    dtrain,
    num_boost_round=300,
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
#print(classification_report(y_test, y_pred, target_names=le.classes_))

# === Step 5: Save model and label encoder ===
model.save_model("xgb_kmer_model_ITS.json")
joblib.dump(le, "species_label_encoder.joblib")

# === Step 6: Plot training log loss ===
import os

# === Step 6: Save Training Curves ===
output_dir = "plot"
os.makedirs(output_dir, exist_ok=True)

epochs = len(evals_result["train"]["mlogloss"])
x_axis = range(epochs)

# === Log loss plot ===
plt.figure(figsize=(10, 5))
plt.plot(x_axis, evals_result["train"]["mlogloss"], label="Train Log Loss")
plt.plot(x_axis, evals_result["test"]["mlogloss"], label="Test Log Loss")
plt.xlabel("Boosting Round")
plt.ylabel("Log Loss")
plt.title("XGBoost Log Loss per Round")
plt.legend()
plt.grid(True)
plt.tight_layout()
loss_plot_path = os.path.join(output_dir, "logloss_plot.png")
plt.savefig(loss_plot_path)
print(f"📊 Saved log loss plot to: {loss_plot_path}")
plt.close()

# === Accuracy per round (only possible with softmax predictions) ===
train_preds = model.predict(dtrain)
train_acc = accuracy_score(y_train, train_preds)

test_preds = model.predict(dtest)
test_acc = accuracy_score(y_test, test_preds)

# Save summary table
summary_df = pd.DataFrame({
    "Metric": ["Train Accuracy", "Test Accuracy", "Best Iteration", "Training Time (s)", "Valid genus count"],
    "Value": [train_acc, test_acc, model.best_iteration, round(end - start, 2), len(valid_species)]
})
summary_csv_path = os.path.join(output_dir, "training_summary.csv")
summary_df.to_csv(summary_csv_path, index=False)
print(f"📋 Saved training summary to: {summary_csv_path}")

# Print summary to terminal
print("\n📈 Training Summary:\n", summary_df)

# Optional: save evals_result to CSV
loss_history_df = pd.DataFrame({
    "Round": x_axis,
    "Train Log Loss": evals_result["train"]["mlogloss"],
    "Test Log Loss": evals_result["test"]["mlogloss"]
})
loss_history_path = os.path.join(output_dir, "loss_per_round.csv")
loss_history_df.to_csv(loss_history_path, index=False)
print(f"📄 Saved loss per round to: {loss_history_path}")
