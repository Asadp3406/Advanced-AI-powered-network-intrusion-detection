"""
Test script for the Flask API
Run this after starting the API server
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_get_classes():
    """Test get classes endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Get Attack Classes")
    print("="*60)
    
    response = requests.get(f"{API_URL}/classes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total classes: {data['total']}")
    print("Classes:", data['classes'])


def test_get_features():
    """Test get features endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Get Required Features")
    print("="*60)
    
    response = requests.get(f"{API_URL}/features")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total features: {data['total']}")
    print("Features:", data['features'][:5], "...")


def test_predict_single():
    """Test single prediction"""
    print("\n" + "="*60)
    print("TEST 4: Single Flow Prediction")
    print("="*60)
    
    # Sample flow data (you should replace with real values)
    flow_data = {
        "Destination Port": 80,
        "Init_Win_bytes_backward": 8192,
        "Bwd Packets/s": 100.5,
        "Init_Win_bytes_forward": 29200,
        "Fwd Packet Length Max": 1460,
        "Avg Bwd Segment Size": 1024,
        "Fwd Packet Length Mean": 800,
        "Average Packet Size": 900,
        "Flow Packets/s": 200,
        "Packet Length Mean": 850,
        "Bwd Packet Length Min": 0,
        "Packet Length Variance": 50000,
        "Flow IAT Mean": 5000,
        "Total Length of Bwd Packets": 10240,
        "Max Packet Length": 1500,
        "Fwd IAT Max": 10000,
        "min_seg_size_forward": 20,
        "Fwd Header Length": 160,
        "Bwd Packet Length Max": 1460,
        "Fwd IAT Total": 50000
    }
    
    response = requests.post(
        f"{API_URL}/predict",
        json=flow_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Prediction: {data['prediction']}")
        print(f"Confidence: {data['confidence']:.4f}")
        print(f"Is Attack: {data['is_attack']}")
        print(f"Top 3 Predictions:")
        for cls, prob in data['top_3_predictions'].items():
            print(f"  {cls}: {prob:.4f}")
    else:
        print(response.json())


def test_predict_csv():
    """Test CSV file prediction"""
    print("\n" + "="*60)
    print("TEST 5: CSV File Prediction")
    print("="*60)
    
    # You need to have a CSV file to test this
    csv_file = "Friday-WorkingHours-Morning.pcap_ISCX.csv"
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            response = requests.post(f"{API_URL}/predict_csv", files=files)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Filename: {data['filename']}")
            print(f"Total flows: {data['total_flows']:,}")
            print(f"Attack count: {data['attack_count']:,}")
            print(f"Benign count: {data['benign_count']:,}")
            print(f"Attack percentage: {data['attack_percentage']}%")
            print(f"\nTop 5 Attacks:")
            for attack, count in data['top_attacks']:
                print(f"  {attack}: {count:,}")
        else:
            print(response.json())
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        print("   Skipping CSV test...")


if __name__ == "__main__":
    print("="*60)
    print("TESTING CIC-IDS2017 API")
    print("="*60)
    print("Make sure the API server is running:")
    print("  python app.py")
    print("="*60)
    
    try:
        test_health_check()
        test_get_classes()
        test_get_features()
        test_predict_single()
        test_predict_csv()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("   Make sure the server is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
