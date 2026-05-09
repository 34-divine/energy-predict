import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

print("Loading dataset...")

dataset_path = os.path.join(os.path.dirname(__file__), '../../dataset/household_power_consumption.txt')

df = pd.read_csv(dataset_path, sep=';', low_memory=False)

print("Dataset loaded. Shape:", df.shape)

print("Cleaning data...")

df.replace('?', np.nan, inplace=True)
df.dropna(inplace=True)

df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M:%S')

df['hour'] = df['datetime'].dt.hour
df['day_of_week'] = df['datetime'].dt.dayofweek
df['month'] = df['datetime'].dt.month

df['Global_active_power'] = pd.to_numeric(df['Global_active_power'])
df['Voltage'] = pd.to_numeric(df['Voltage'])
df['Sub_metering_1'] = pd.to_numeric(df['Sub_metering_1'])
df['Sub_metering_2'] = pd.to_numeric(df['Sub_metering_2'])
df['Sub_metering_3'] = pd.to_numeric(df['Sub_metering_3'])

print("Data cleaned. Rows remaining:", len(df))

features = ['hour', 'day_of_week', 'month', 'Voltage', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
target = 'Global_active_power'

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Linear Regression...")
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_mae = mean_absolute_error(y_test, lr_pred)
lr_r2 = r2_score(y_test, lr_pred)
print(f"Linear Regression - MAE: {lr_mae:.4f}, R2: {lr_r2:.4f}")

print("Training Random Forest...")
rf = RandomForestRegressor(n_estimators=10, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_mae = mean_absolute_error(y_test, rf_pred)
rf_r2 = r2_score(y_test, rf_pred)
print(f"Random Forest - MAE: {rf_mae:.4f}, R2: {rf_r2:.4f}")

if rf_r2 > lr_r2:
    best_model = rf
    best_name = "Random Forest"
else:
    best_model = lr
    best_name = "Linear Regression"

print(f"Best model: {best_name}")

model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
joblib.dump(best_model, model_path)

features_path = os.path.join(os.path.dirname(__file__), 'features.pkl')
joblib.dump(features, features_path)

print(f"Model saved to {model_path}")
print("Training complete.")