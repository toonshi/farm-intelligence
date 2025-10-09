import pandas as pd
from sklearn.model_selection import train_test_split

# Load the dataset
df = pd.read_csv('data/mshamba_merged.csv')

# --- 1. Handle Missing Data ---

# For numerical columns, fill with the median
for col in ['Planted Area (Acres)', 'Yield (Kg)', 'Market Price (KES/Kg)', 'Revenue (KES)', 'Cost of Production (KES)', 'Profit (KES)']:
    if col in df.columns:
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)

# For categorical columns, fill with the mode
for col in ['Crop Type', 'Crop Variety', 'Season', 'Soil Type', 'Irrigation Method', 'Fertilizer Used', 'Pest Control', 'Weather Impact']:
    if col in df.columns:
        mode_val = df[col].mode()[0]
        df[col].fillna(mode_val, inplace=True)

# --- 2. Feature Engineering (One-Hot Encoding) ---

# Select categorical columns for one-hot encoding
categorical_cols = ['Crop Type', 'County', 'Season', 'Soil Type', 'Irrigation Method', 'Fertilizer Used', 'Pest Control', 'Weather Impact']
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# --- 3. Feature Selection ---

# Select features (X) and target (y)
features = [
    'Planted Area (Acres)',
    'Market Price (KES/Kg)',
] + [col for col in df_encoded.columns if any(cat_col in col for cat_col in categorical_cols)]

target = 'Yield (Kg)'

X = df_encoded[features]
y = df_encoded[target]

# --- 4. Split the data ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- 5. Save the data ---
# For simplicity, we'll save the split data into separate files
X_train.to_csv('data/X_train_merged.csv', index=False)
X_test.to_csv('data/X_test_merged.csv', index=False)
y_train.to_csv('data/y_train_merged.csv', index=False)
y_test.to_csv('data/y_test_merged.csv', index=False)

print("Data preparation complete. The following files have been created in the 'data' directory:")
print("- X_train_merged.csv")
print("- X_test_merged.csv")
print("- y_train_merged.csv")
print("- y_test_merged.csv")
