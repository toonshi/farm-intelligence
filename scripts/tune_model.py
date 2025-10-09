import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
import joblib

# --- 1. Load the data ---
X_train = pd.read_csv('data/X_train.csv')
y_train = pd.read_csv('data/y_train.csv')

# --- 2. Define the hyperparameter grid ---
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# --- 3. Perform Grid Search ---
print("Performing Grid Search...")
rf = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train.values.ravel())

# --- 4. Print the best parameters ---
print("Best parameters found:")
print(grid_search.best_params_)

# --- 5. Train and save the best model ---
print("Training and saving the best model...")
best_model = grid_search.best_estimator_
joblib.dump(best_model, 'yield_predictor_tuned.joblib')

print("Tuned model saved to yield_predictor_tuned.joblib")
