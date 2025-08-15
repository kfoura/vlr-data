import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
import numpy as np

df = pd.read_csv(r"C:\Users\kauda\Documents\Coding\vlr-data\vlr-data\ML pipeline\player_stats.csv")

# Convert percentage to numerical
df['all_HS'] = df["all_HS"].astype(str)
df['all_HS'] = df['all_HS'].str.replace("%", "")
df['all_HS'] = pd.to_numeric(df["all_HS"], errors='coerce')
df['all_HS'] = df["all_HS"] / 100
df['all_KAST'] = df["all_KAST"].astype(str)
df['all_KAST'] = df['all_KAST'].str.replace("%", "")
df['all_KAST'] = pd.to_numeric(df["all_KAST"], errors='coerce')
df['all_KAST'] = df["all_KAST"] / 100

# Sometimes, ACS gets put in instead of rating for that column
condition = df['all_Rating'] <= 3
df = df[condition]

features = ["team",
            "agent",
            "all_Rating",
            "all_ACS",
            "all_KAST",
            "all_ADR",
            "all_HS",
            "map",
            "enemy_team"]

target = "all_Kills"

X = df[features]
y = df[target]

# --------------------
# Train/Test Split
# --------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size = 0.2, random_state=42
)

# --------------------
# Preprocessing
# --------------------

categorical_cols = ["team", "agent", "map", "enemy_team"]
numerical_cols = [col for col in features if col not in categorical_cols]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ("num", "passthrough", numerical_cols)
    ]
)

# --------------------
# Model
# --------------------

model = xgb.XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", model)
])


# --------------------
# Train
# --------------------

pipeline.fit(X_train, y_train)

# --------------------
# Predict
# --------------------

y_pred = pipeline.predict(X_test)

# Evaluation

epsilon = 1e-6
mae = mean_absolute_error(y_test, y_pred)
mape = np.mean(np.abs((y_test - y_pred) / (y_test + epsilon))) * 100
print(f"Mean absolute Error: {mae:.2f} kills")
print(f"Mean Absolute Percentage Error: {mape:.2f}%")

# --------------------
# Output projected kills
# --------------------

results = X_test.copy()
results["Actual_Kills"] = y_test
results["Projected_Kills"] = y_pred.round(2)

# Sort by highest
results_sorted = results.sort_values(by="Projected_Kills", ascending=False)
results_sorted.to_csv("projected_kills.csv", index=False)
print("Projected Kills saved")