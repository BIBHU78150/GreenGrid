
from flask import Flask, jsonify, request
from flask_cors import CORS
from model import predict_usage, generate_synthetic_data, train_model
import random
from datetime import datetime

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Ensure model exists on startup
try:
    train_model()
except Exception as e:
    print(f"Error training model: {e}")

@app.route('/api/status', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "GreenGrid API is running"})

@app.route('/api/usage', methods=['GET'])
def get_usage():
    """Returns mock historical usage for the chart."""
    # Generate 24 hours of data for a "typical" day
    data = []
    current_hour = datetime.now().hour
    
    # Simple simulation: 24 data points
    for hour in range(24):
        # Temp varies by hour (cooler at night, hotter at noon)
        temp = 25 + (10 * np.sin((hour - 6) * np.pi / 12)) 
        usage = predict_usage(hour, temp, is_weekend=0)
        data.append({
            "hour": f"{hour}:00",
            "usage": usage,
            "temperature": round(temp, 1)
        })
    
    return jsonify(data)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict usage based on user inputs."""
    data = request.json
    try:
        hour = int(data.get('hour', 12))
        temp = float(data.get('temperature', 30))
        is_weekend = int(data.get('is_weekend', 0))
        
        prediction = predict_usage(hour, temp, is_weekend)
        
        return jsonify({
            "predicted_usage": prediction,
            "inputs": {
                "hour": hour,
                "temperature": temp,
                "is_weekend": is_weekend
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Return tips based on simulated current load."""
    # Randomly simulate high or low load context
    load_context = random.choice(["high", "medium", "low"])
    
    if load_context == "high":
        tips = [
            {"id": 1, "text": "High usage detected! Turn off AC in empty classrooms.", "category": "Urgent"},
            {"id": 2, "text": "Dim hallway lights by 50% to reduce load.", "category": "Lighting"}
        ]
    elif load_context == "medium":
        tips = [
            {"id": 3, "text": "Usage is normal. Check Library thermostat setpoint.", "category": "Optimization"},
            {"id": 4, "text": "Ensure computer labs are in power-saving mode.", "category": "IT"}
        ]
    else:
        tips = [
            {"id": 5, "text": "Great job! Usage is low. Maintenance time?", "category": "Info"},
            {"id": 6, "text": "Inspect solar panels for efficiency.", "category": "Maintenance"}
        ]
        
    return jsonify({
        "context": load_context,
        "recommendations": tips
    })

@app.route('/api/system_status', methods=['POST'])
def get_system_status():
    """Determine state of systems based on inputs."""
    data = request.json
    hour = int(data.get('hour', 12))
    temp = float(data.get('temperature', 25))
    
    # Logic for Streetlights
    # ON if 6PM (18) to 6AM (6)
    lights_on = (hour >= 18) or (hour < 6)
    
    # Logic for AC
    # ON if Temp > 25
    ac_on = temp > 25
    
    return jsonify({
        "streetlights": "ON" if lights_on else "OFF",
        "ac_system": "ON" if ac_on else "OFF",
        "message": "Systems auto-adjusted based on environment."
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_grid():
    """Simulate load shedding."""
    return jsonify({
        "status": "Optimized",
        "actions": [
            "Dimmed Streetlights by 20%",
            "Set AC to Eco-Mode (26°C)",
            "Shifted Non-Essential Loads"
        ],
        "savings_estimated": "15%"
    })

if __name__ == '__main__':
    # Need to import numpy here if used inside functions but not at top level?
    # Actually used in get_usage
    import numpy as np
    app.run(debug=True, port=5000)
