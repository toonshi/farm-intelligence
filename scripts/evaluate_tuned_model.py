import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# --- 1. Load the data ---
X_test = pd.read_csv('data/X_test.csv')
y_test = pd.read_csv('data/y_test.csv')

# --- 2. Load the tuned model ---
print("Loading tuned model...")
tuned_model = joblib.load('yield_predictor_tuned.joblib')

# --- 3. Evaluate the model ---
print("Evaluating tuned model...")
y_pred = tuned_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Tuned Model Mean Absolute Error (MAE): {mae}")
print(f"Tuned Model R-squared (R2): {r2}")
