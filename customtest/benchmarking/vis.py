import matplotlib.pyplot as plt
import pandas as pd

# Sample data (replace with actual values or load from CSVs)
data = {
    "Model": ["MatK Classifier", "rbcL Classifier", "ITS Classifier"],
    "Train Accuracy": [0.9994818652849741, 0.9987333755541482, 0.9983960243655952],
    "Test Accuracy": [0.8975155279503105, 0.8860759493670886, 0.9076209901724458]
}

df = pd.DataFrame(data)

# Plot grouped bars
x = range(len(df))
bar_width = 0.35

fig, ax = plt.subplots(figsize=(8, 6))
bars1 = ax.bar([i - bar_width / 2 for i in x], df["Train Accuracy"], width=bar_width, label="Train Accuracy")
bars2 = ax.bar([i + bar_width / 2 for i in x], df["Test Accuracy"], width=bar_width, label="Test Accuracy")

# Labels and styling
ax.set_xticks(x)
ax.set_xticklabels(df["Model"])
ax.set_ylabel("Accuracy")
ax.set_title("Train vs Test Accuracy for Models")
ax.legend()
ax.grid(True, axis='y', linestyle='--', alpha=0.6)

# Annotate bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.005, f"{height:.2f}", ha='center', va='bottom')

plt.tight_layout()
plt.show()
