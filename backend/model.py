
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

MODEL_PATH = 'energy_model.pkl'

def generate_synthetic_data(n_samples=1000):
    """
    Generates synthetic energy usage data.
    Features: 
    - Hour (0-23)
    - Temperature (20-40 C)
    - Is_Weekend (0 or 1)
    
    Target:
    - Energy_Usage (kWh)
    """
    np.random.seed(42)
    hours = np.random.randint(0, 24, n_samples)
    temps = np.random.uniform(20, 40, n_samples)
    is_weekend = np.random.randint(0, 2, n_samples)
    
    # Logic: 
    # - Peak usage between 9 AM (9) and 5 PM (17).
    # - Higher temp -> Higher AC usage -> Higher energy.
    # - Weekends -> Lower usage (campus closed/less active).
    
    usage = 50 + (10 * np.sin((hours - 9) * np.pi / 12)) + (2 * temps) - (20 * is_weekend) + np.random.normal(0, 5, n_samples)
    usage = np.maximum(usage, 0) # Ensure no negative usage
    
    df = pd.DataFrame({
        'Hour': hours,
        'Temperature': temps,
        'Is_Weekend': is_weekend,
        'Energy_Usage': usage
    })
    return df

def train_model():
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    
    X = df[['Hour', 'Temperature', 'Is_Weekend']]
    y = df['Energy_Usage']
    
    model = LinearRegression()
    model.fit(X, y)
    
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

def load_model():
    if not os.path.exists(MODEL_PATH):
        return train_model()
    return joblib.load(MODEL_PATH)

def predict_usage(hour, temp, is_weekend=0):
    model = load_model()
    # Ensure input is 2D array
    prediction = model.predict([[hour, temp, is_weekend]])
    return max(0, round(prediction[0], 2))

if __name__ == "__main__":
    train_model()
