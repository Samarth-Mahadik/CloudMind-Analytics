import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import os

# ---------- Paths ----------
cost_estimation_path = "output/analysis/cost_estimation.json"
aws_history_path = "output/aws_cost_history.csv"
prediction_output_path = "output/predictions"
os.makedirs(prediction_output_path, exist_ok=True)

# ---------- Step 1: Check cost_estimation.json ----------
if not os.path.exists(cost_estimation_path):
    print("❌ cost_estimation.json not found. Run Day 4 module first.")
    exit()

with open(cost_estimation_path, "r") as f:
    cost_data = json.load(f)

print("\n✅ Loaded cost_estimation.json data:")
print(cost_data)

# ---------- Step 2: Load AWS real cost history ----------
if not os.path.exists(aws_history_path):
    print("❌ aws_cost_history.csv not found. Please add your historical cost CSV.")
    exit()

# Read CSV and skip first summary row if present
aws_df = pd.read_csv(aws_history_path, skiprows=1)

# Dynamic column handling: rename first column to 'Date' if needed
if aws_df.columns[0].lower() not in ["date", "billingdate"]:
    aws_df.rename(columns={aws_df.columns[0]: "Date"}, inplace=True)

# Select numeric cost columns automatically
numeric_cols = aws_df.select_dtypes(include=["float64", "int64"]).columns.tolist()
resource_cols = [col for col in numeric_cols if col.lower() not in ["total costs($)"]]  # exclude total

# Keep only Date + selected resources
aws_df = aws_df[["Date"] + resource_cols]

# Convert Date to datetime safely
aws_df["Date"] = pd.to_datetime(aws_df["Date"], dayfirst=True, errors='coerce')
invalid_dates = aws_df["Date"].isna().sum()
if invalid_dates > 0:
    print(f"⚠️ {invalid_dates} invalid date rows found. Dropping them.")
aws_df = aws_df.dropna(subset=["Date"])

# Convert resource columns to numeric, fill missing with 0
for col in resource_cols:
    aws_df[col] = pd.to_numeric(aws_df[col], errors='coerce').fillna(0)

print("\n✅ Loaded and processed AWS cost history:")
print(aws_df.head())

# ---------- Step 3: Prepare trend DataFrame ----------
trend_df = aws_df.copy()
trend_df["Day"] = (trend_df["Date"] - trend_df["Date"].min()).dt.days + 1

# ---------- Step 4: Predict future cost using Linear Regression ----------
predictions = {}

for resource in resource_cols:
    X = trend_df["Day"].values.reshape(-1, 1)
    y = trend_df[resource].values

    # Skip resource if all values are zero (no cost data)
    if np.all(y == 0):
        print(f"⚠️ Resource '{resource}' has all zero values. Skipping prediction.")
        continue

    model = LinearRegression()
    model.fit(X, y)

    future_day = np.array([[trend_df["Day"].max() + 3]])  # predict 3 days after last available day
    predicted_cost = model.predict(future_day)[0]

    # Fix divide by zero for ChangePercent
    if y[-1] == 0:
        change_percent = 0.0  # avoid Infinity
    else:
        change_percent = round(((predicted_cost - y[-1]) / y[-1]) * 100, 2)

    predictions[resource] = {
        "PredictedFutureCost": round(float(predicted_cost), 2),
        "CurrentCost": round(float(y[-1]), 2),
        "ChangePercent": change_percent
    }

# ---------- Step 5: Save predictions ----------
with open(os.path.join(prediction_output_path, "ml_cost_predictions.json"), "w") as f:
    json.dump(predictions, f, indent=4)

print("\n✅ ML Prediction Complete. Results saved to output/predictions/ml_cost_predictions.json")
