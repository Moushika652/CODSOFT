import requests
import json

# Test data for predictions
test_data = [
    {"TV": 150.0, "Radio": 75.0, "Newspaper": 50.0},
    {"TV": 200.0, "Radio": 100.0, "Newspaper": 75.0},
    {"TV": 100.0, "Radio": 50.0, "Newspaper": 25.0}
]

base_url = "http://localhost:5000"

print("Making test predictions...")
for i, data in enumerate(test_data):
    try:
        response = requests.post(f"{base_url}/predict", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Prediction {i+1}: ₹{result['prediction']:.2f}")
            print(f"  ID: {result['prediction_id']}")
            print(f"  Timestamp: {result['timestamp']}")
        else:
            print(f"Error in prediction {i+1}: {response.status_code}")
    except Exception as e:
        print(f"Exception in prediction {i+1}: {e}")

print("\nTesting dashboard endpoints...")
try:
    # Test time series analysis
    response = requests.get(f"{base_url}/time-series-analysis")
    print(f"Time series status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Total predictions: {data['statistics']['total_predictions']}")
    else:
        print(f"  Error: {response.text}")

    # Test comparison
    response = requests.get(f"{base_url}/prediction-comparison")
    print(f"Comparison status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Average sales: ₹{data['summary']['average_sales']:.2f}")
    else:
        print(f"  Error: {response.text}")

except Exception as e:
    print(f"Exception testing endpoints: {e}")

print("\nTest complete!")
