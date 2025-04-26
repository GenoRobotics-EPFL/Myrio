import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV file
df = pd.read_csv('customtest/benchmarking/metrics.csv')  # Replace with your file path

# Add a column to label the model (assuming file is stacked model-wise)
# Modify this depending on your actual file layout
num_metrics = df['Metric'].nunique()
df['Model'] = ['Model1'] * num_metrics + ['Model2'] * num_metrics + ['Model3'] * num_metrics

# Pivot for easier plotting
pivot_df = df.pivot(index='Metric', columns='Model', values='Value')

# Plot grouped bar chart
pivot_df.plot(kind='bar', figsize=(10, 6))

plt.title('Model Performance Comparison')
plt.ylabel('Value')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Model')
plt.tight_layout()
plt.grid(axis='y')

# Save or show plot
plt.savefig('model_comparison.png', dpi=300)
plt.show()
