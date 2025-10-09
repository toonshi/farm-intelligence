import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('data/mshamba_clean_seasons.csv')

# Display basic information
print("Dataframe Info:")
df.info()

print("\nDataframe Description:")
print(df.describe())

# Display correlation matrix
# We need to select only numeric columns for correlation matrix
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
corr_matrix = df[numeric_cols].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Correlation Matrix of Numeric Features')
plt.savefig('correlation_matrix.png')

print("\nCorrelation matrix saved to correlation_matrix.png")

