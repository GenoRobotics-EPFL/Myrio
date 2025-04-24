import pandas as pd
import xgboost as xgb
import joblib
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D  # Needed for 3D plotting

# === Load model and label encoder ===
# Measure time
import time
start_time = time.time()
model = xgb.Booster()
model.load_model("customtest/trained_models/xgb_kmer_model_matK.json")

label_encoder = joblib.load("customtest/species_label_encoder.joblib")

# === Load your custom dataset ===
X = pd.read_parquet("customtest/generated_dataset/generated.parquet")
X_custom = X.drop(columns=["genus"], errors="ignore")  # features only

# === Convert to DMatrix and predict ===
dcustom = xgb.DMatrix(X_custom)
y_pred_indices = model.predict(dcustom).astype(int)
y_pred_labels = label_encoder.inverse_transform(y_pred_indices)
print(f"Predicted labels: {y_pred_labels}")

time_taken = time.time() - start_time
print(f"Time taken to predict: {time_taken:.2f} seconds")

# === Add predictions to original DataFrame ===
X["predicted_species"] = y_pred_labels
X.to_csv("custom_predictions.csv", index=False)

# === Per-Class Accuracy Bar Plot ===
# === Filtered Per-Class Accuracy Plot (only <75%) ===
print("📊 Calculating per-class accuracy (filtering <75%)...")

if "species" in X.columns and "predicted_species" in X.columns:
    X["correct"] = X["species"] == X["predicted_species"]

    # Compute accuracy per species
    acc_per_species = X.groupby("species")["correct"].mean()

    # Filter for species with accuracy < 75%
    low_acc = acc_per_species[acc_per_species > 0.75].sort_values()

    if low_acc.empty:
        print("✅ No species with accuracy < 75%")
    else:
        # Plot
        plt.figure(figsize=(14, 6))
        sns.barplot(x=low_acc.index, y=low_acc.values, color="salmon")
        plt.xticks(rotation=90)
        plt.xlabel("Species")
        plt.ylabel("Accuracy")
        plt.title("Per-Class Accuracy (Only <75%)")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.show()

        # Print worst performing classes
        print("\n📉 Species with lowest accuracy (<75%):")
        print(low_acc.head(10))
else:
    print("⚠️ 'species' or 'predicted_species' column missing. Skipping per-class accuracy.")
