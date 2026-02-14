import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv("industrial_fault_detection_data_1000.csv")

# Convert timestamp column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Drop RMS Vibration column if already present
df.drop(columns=['RMS Vibration'], inplace=True, errors='ignore')

# Recalculate RMS Vibration
df['RMS Vibration'] = np.sqrt(df['Vibration (mm/s)'] ** 2)

# Fault severity mapping
severity_map = {
    0: 'LOW',      # No Fault
    1: 'MEDIUM',   # Bearing Fault
    2: 'HIGH'      # Overheating
}

df['Severity'] = df['Fault Label'].map(severity_map)

# Display dataset information
print(df.info())
print(df[['RMS Vibration']].describe())
print(df.isnull().sum())

# Save preprocessed dataset
df.to_csv("industrial_iot_preprocessed.csv", index=False)