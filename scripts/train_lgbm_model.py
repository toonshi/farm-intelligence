import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import re

# --- 1. Load the data ---
X_train = pd.read_csv('data/X_train_merged_v2.csv')
X_test = pd.read_csv('data/X_test_merged_v2.csv')
y_train = pd.read_csv('data/y_train_merged_v2.csv')
y_test = pd.read_csv('data/y_test_merged_v2.csv')

# --- Clean column names ---
X_train.columns = [re.sub(r'[^A-Za-z0-9_]+', '', col) for col in X_train.columns]
X_test.columns = [re.sub(r'[^A-Za-z0-9_]+', '', col) for col in X_test.columns]

# --- 2. Train the model ---
print("Training LightGBM model...")
model = lgb.LGBMRegressor(random_state=42)
model.fit(X_train, y_train.values.ravel())

# --- 3. Evaluate the model ---
print("Evaluating model...")
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"R-squared (R2): {r2}")

# --- 4. Save the model ---
print("Saving model to yield_predictor_lgbm.joblib...")
joblib.dump(model, 'yield_predictor_lgbm.joblib')

print("Model training complete.")