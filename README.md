# 🛡️ Network Intrusion Detection System

Advanced AI-powered network intrusion detection using the CIC-IDS2017 dataset with Random Forest classifier enhanced by SMOTE.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Accuracy](https://img.shields.io/badge/Accuracy-99.80%25-brightgreen.svg)
![F1 Score](https://img.shields.io/badge/Macro%20F1-0.8598-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📊 Project Overview

This project implements a multi-class network intrusion detection system capable of identifying 15 different types of network attacks with 99.80% accuracy. The system uses machine learning to analyze network traffic patterns and detect malicious activities in real-time.

### Key Features

- ✅ **High Accuracy**: 99.80% classification accuracy
- ✅ **Multi-Class Detection**: Identifies 15 different attack types
- ✅ **SMOTE Enhanced**: Improved minority class detection
- ✅ **REST API**: Easy integration with existing systems
- ✅ **Web Dashboard**: Beautiful dark-themed UI for analysis
- ✅ **Real-time Processing**: Fast inference (<1 second per file)
- ✅ **Production Ready**: Deployable with Docker/Gunicorn

## 🎯 Attack Types Detected

1. **BENIGN** - Normal traffic
2. **Bot** - Botnet traffic
3. **DDoS** - Distributed Denial of Service
4. **DoS Hulk** - DoS attack variant
5. **DoS GoldenEye** - DoS attack variant
6. **DoS Slowhttptest** - Slow HTTP DoS
7. **DoS slowloris** - Slowloris DoS
8. **FTP-Patator** - FTP brute force
9. **SSH-Patator** - SSH brute force
10. **PortScan** - Port scanning activity
11. **Infiltration** - Network infiltration
12. **Web Attack - Brute Force**
13. **Web Attack - XSS**
14. **Web Attack - SQL Injection**
15. **Heartbleed** - Heartbleed vulnerability exploit

## 📈 Performance Metrics

| Metric | Score |
|--------|-------|
| **Test Accuracy** | 99.80% |
| **Macro F1 Score** | 0.8598 |
| **Weighted F1 Score** | 0.9982 |
| **Training Samples** | 2.8M flows |
| **Features Used** | 20 (selected from 83) |
| **Model Size** | 522.3 MB |

### Per-Class Performance

| Attack Type | Precision | Recall | F1-Score |
|-------------|-----------|--------|----------|
| BENIGN | 0.9997 | 0.9983 | 0.9990 |
| Bot | 0.6808 | 0.9317 | 0.7867 |
| DDoS | 0.9997 | 0.9996 | 0.9997 |
| DoS Hulk | 0.9984 | 0.9993 | 0.9988 |
| PortScan | 0.9936 | 0.9969 | 0.9953 |
| FTP-Patator | 1.0000 | 0.9983 | 0.9992 |
| SSH-Patator | 1.0000 | 0.9977 | 0.9989 |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 2GB free disk space

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/network-intrusion-detection.git
cd network-intrusion-detection
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download the dataset** (Optional - for training)

Place CIC-IDS2017 CSV files in the project directory or download from [Kaggle](https://www.kaggle.com/datasets/cicdataset/cicids2017).

### Running the Application

#### Option 1: Web Dashboard (Recommended)

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

#### Option 2: API Only

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 3: Train Your Own Model

```bash
python run_improved.py
```

## 📡 API Usage

### Health Check
```bash
curl http://localhost:5000/api
```

### Predict Single Flow
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Destination Port": 80,
    "Init_Win_bytes_backward": 8192,
    ...
  }'
```

### Upload CSV File
```bash
curl -X POST http://localhost:5000/predict_csv \
  -F "file=@traffic.csv"
```

### Python Client Example
```python
import requests

# Analyze CSV file
with open('network_traffic.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/predict_csv',
        files={'file': f}
    )
    
results = response.json()
print(f"Total flows: {results['total_flows']}")
print(f"Attacks detected: {results['attack_count']}")
```

## 🏗️ Project Structure

```
network-intrusion-detection/
├── app.py                          # Flask API server
├── run_improved.py                 # Model training script
├── test_api.py                     # API testing script
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Web dashboard
├── model_improved.pkl              # Trained model (522MB)
├── label_encoder_improved.pkl      # Label encoder
├── selected_features_improved.pkl  # Feature list
├── metrics_improved.pkl            # Performance metrics
├── CIC_IDS2017_Clean.ipynb        # Jupyter notebook
└── *.csv                          # Dataset files (not in repo)
```

## 🔬 Technical Details

### Model Architecture

- **Algorithm**: Random Forest Classifier
- **Trees**: 100 estimators
- **Max Depth**: 35
- **Class Weighting**: Balanced subsample
- **Feature Selection**: Top 20 from 83 using importance scores

### Data Processing Pipeline

1. **Data Loading**: Merge multiple CSV files
2. **Cleaning**: Handle infinity/NaN values
3. **Feature Selection**: Random Forest importance + Mutual Information
4. **Class Balancing**: SMOTE oversampling for minority classes
5. **Training**: GridSearchCV with 3-fold cross-validation
6. **Evaluation**: Comprehensive metrics on test set

### Key Improvements (SMOTE Enhanced)

- **Bot Detection**: 37.68% → 78.67% F1 (+109%)
- **Heartbleed**: 0% → 100% F1 (Perfect detection)
- **SQL Injection**: 0% → 40% F1
- **Infiltration**: 57.14% → 88.89% F1 (+56%)

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t intrusion-detection .
```

### Run Container
```bash
docker run -p 5000:5000 intrusion-detection
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
```

## 📊 Dataset Information

**Source**: CIC-IDS2017 (Canadian Institute for Cybersecurity)

- **Total Flows**: 2,830,743
- **Features**: 83 (Flow Duration, Packet Stats, IAT, TCP Flags, etc.)
- **Classes**: 15 (1 benign + 14 attack types)
- **Time Period**: 5 days of network traffic
- **Format**: CSV files (one per day/attack type)

## 🧪 Testing

Run the test suite:
```bash
python test_api.py
```

Expected output:
- ✅ Health check passed
- ✅ API endpoints working
- ✅ CSV file analysis successful
- ✅ Predictions accurate

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=production
export MODEL_PATH=model_improved.pkl
export PORT=5000
```

### Model Parameters
Edit `run_improved.py` to customize:
- `USE_SMOTE`: Enable/disable SMOTE
- `SAMPLE_FRACTION`: Use subset of data for testing
- `param_grid`: Hyperparameter search space

## 📝 Training Your Own Model

1. **Prepare Dataset**: Place CSV files in project directory
2. **Configure Settings**: Edit `run_improved.py`
3. **Start Training**:
```bash
python run_improved.py
```

Training time: ~35 minutes on 16-core CPU

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Dataset**: CIC-IDS2017 by Canadian Institute for Cybersecurity
- **Libraries**: Scikit-learn, Flask, Pandas, NumPy, imbalanced-learn
- **Inspiration**: Network security research community

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

## 🔗 Links

- [CIC-IDS2017 Dataset](https://www.unb.ca/cic/datasets/ids-2017.html)
- [Research Paper](https://www.sciencedirect.com/science/article/pii/S2352340918300057)
- [Kaggle Dataset](https://www.kaggle.com/datasets/cicdataset/cicids2017)

---

**⭐ If you find this project useful, please consider giving it a star!**
