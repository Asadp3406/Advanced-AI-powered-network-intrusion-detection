"""
Flask API for CIC-IDS2017 Network Intrusion Detection
Deploy this to classify network traffic in real-time
"""

from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load model and artifacts at startup
print("Loading model...")
MODEL_PATH = 'model_improved.pkl'
ENCODER_PATH = 'label_encoder_improved.pkl'
FEATURES_PATH = 'selected_features_improved.pkl'

try:
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    selected_features = joblib.load(FEATURES_PATH)
    print(f"✅ Model loaded successfully!")
    print(f"   Features: {len(selected_features)}")
    print(f"   Classes: {len(encoder.classes_)}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    encoder = None
    selected_features = None


@app.route('/')
def home():
    """Web dashboard"""
    return render_template('index.html')


@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'status': 'online',
        'model': 'CIC-IDS2017 Network Intrusion Detection',
        'version': '2.0 (Improved with SMOTE)',
        'accuracy': '99.80%',
        'macro_f1': '0.8598',
        'endpoints': {
            '/': 'Web Dashboard',
            '/api': 'API information',
            '/predict': 'POST - Predict single flow',
            '/predict_batch': 'POST - Predict multiple flows',
            '/predict_csv': 'POST - Upload CSV file',
            '/classes': 'GET - List attack classes',
            '/features': 'GET - List required features'
        }
    })


@app.route('/classes', methods=['GET'])
def get_classes():
    """Get list of attack classes"""
    if encoder is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'classes': encoder.classes_.tolist(),
        'total': len(encoder.classes_)
    })


@app.route('/features', methods=['GET'])
def get_features():
    """Get list of required features"""
    if selected_features is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'features': selected_features,
        'total': len(selected_features)
    })


@app.route('/predict', methods=['POST'])
def predict_single():
    """
    Predict attack type for a single network flow
    
    Request body (JSON):
    {
        "Destination Port": 80,
        "Init_Win_bytes_backward": 8192,
        "Bwd Packets/s": 100.5,
        ... (all 20 features)
    }
    
    Response:
    {
        "prediction": "DDoS",
        "confidence": 0.95,
        "probabilities": {...}
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        # Create DataFrame with single row
        df = pd.DataFrame([data])
        
        # Ensure all features are present
        missing_features = [f for f in selected_features if f not in df.columns]
        if missing_features:
            return jsonify({
                'error': 'Missing features',
                'missing': missing_features
            }), 400
        
        # Extract features in correct order
        X = df[selected_features].values.astype(np.float32)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Predict
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Get class name
        predicted_class = encoder.inverse_transform([prediction])[0]
        confidence = float(probabilities[prediction])
        
        # Get top 3 predictions
        top_3_idx = np.argsort(probabilities)[-3:][::-1]
        top_3 = {
            encoder.inverse_transform([idx])[0]: float(probabilities[idx])
            for idx in top_3_idx
        }
        
        return jsonify({
            'prediction': predicted_class,
            'confidence': confidence,
            'top_3_predictions': top_3,
            'is_attack': predicted_class != 'BENIGN'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    """
    Predict attack types for multiple network flows
    
    Request body (JSON):
    {
        "flows": [
            {"Destination Port": 80, ...},
            {"Destination Port": 443, ...},
            ...
        ]
    }
    
    Response:
    {
        "predictions": ["DDoS", "BENIGN", ...],
        "summary": {...}
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        flows = data.get('flows', [])
        
        if not flows:
            return jsonify({'error': 'No flows provided'}), 400
        
        # Create DataFrame
        df = pd.DataFrame(flows)
        
        # Ensure all features are present
        missing_features = [f for f in selected_features if f not in df.columns]
        if missing_features:
            # Fill missing features with 0
            for f in missing_features:
                df[f] = 0
        
        # Extract features
        X = df[selected_features].values.astype(np.float32)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Predict
        predictions = model.predict(X)
        predicted_classes = encoder.inverse_transform(predictions)
        
        # Summary
        unique, counts = np.unique(predicted_classes, return_counts=True)
        summary = {cls: int(count) for cls, count in zip(unique, counts)}
        
        attack_count = sum(count for cls, count in summary.items() if cls != 'BENIGN')
        
        return jsonify({
            'total_flows': len(flows),
            'predictions': predicted_classes.tolist(),
            'summary': summary,
            'attack_count': attack_count,
            'benign_count': summary.get('BENIGN', 0),
            'attack_percentage': round((attack_count / len(flows)) * 100, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_csv', methods=['POST'])
def predict_csv():
    """
    Upload CSV file and get predictions
    
    Request: multipart/form-data with 'file' field
    
    Response:
    {
        "total_flows": 1000,
        "predictions": [...],
        "summary": {...}
    }
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Read CSV
        df = pd.read_csv(file, low_memory=False, encoding='cp1252')
        df.columns = df.columns.str.strip()
        
        # Preprocess
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)
        
        # Ensure all features are present
        missing_features = [f for f in selected_features if f not in df.columns]
        for f in missing_features:
            df[f] = 0
        
        # Convert to numeric
        for col in selected_features:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(np.float32)
        
        # Extract features
        X = df[selected_features].values.astype(np.float32)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Predict
        predictions = model.predict(X)
        predicted_classes = encoder.inverse_transform(predictions)
        
        # Summary
        unique, counts = np.unique(predicted_classes, return_counts=True)
        summary = {cls: int(count) for cls, count in zip(unique, counts)}
        
        attack_count = sum(count for cls, count in summary.items() if cls != 'BENIGN')
        
        # Calculate percentages
        summary_with_pct = {
            cls: {
                'count': int(count),
                'percentage': round((count / len(predicted_classes)) * 100, 2)
            }
            for cls, count in summary.items()
        }
        
        return jsonify({
            'filename': file.filename,
            'total_flows': len(predicted_classes),
            'summary': summary_with_pct,
            'attack_count': attack_count,
            'benign_count': summary.get('BENIGN', 0),
            'attack_percentage': round((attack_count / len(predicted_classes)) * 100, 2),
            'top_attacks': sorted(
                [(cls, count) for cls, count in summary.items() if cls != 'BENIGN'],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
