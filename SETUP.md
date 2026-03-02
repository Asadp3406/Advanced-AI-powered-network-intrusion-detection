# Setup Guide

## Model Files

The trained model files are too large for GitHub (522MB). You have three options:

### Option 1: Download Pre-trained Model

Download the model files from:
- [Google Drive Link] (Add your link here)
- [Dropbox Link] (Add your link here)

Place these files in the project root:
- `model_improved.pkl`
- `label_encoder_improved.pkl`
- `selected_features_improved.pkl`

### Option 2: Train Your Own Model

1. Download the CIC-IDS2017 dataset from [Kaggle](https://www.kaggle.com/datasets/cicdataset/cicids2017)

2. Place CSV files in the project directory

3. Run the training script:
```bash
python run_improved.py
```

Training will take approximately 35 minutes on a 16-core CPU.

### Option 3: Use Git LFS (Large File Storage)

If you have Git LFS installed:

```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes
git add *.pkl
git commit -m "Add model files"
git push
```

## Dataset Files

The dataset CSV files are also too large for GitHub. Download them from:
- [CIC-IDS2017 Official](https://www.unb.ca/cic/datasets/ids-2017.html)
- [Kaggle Mirror](https://www.kaggle.com/datasets/cicdataset/cicids2017)

Required files:
- Monday-WorkingHours.pcap_ISCX.csv
- Tuesday-WorkingHours.pcap_ISCX.csv
- Wednesday-workingHours.pcap_ISCX.csv
- Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
- Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
- Friday-WorkingHours-Morning.pcap_ISCX.csv
- Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
- Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv

## Quick Start After Setup

1. Ensure model files are in place
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open browser to `http://localhost:5000`

## Troubleshooting

### Model Not Found Error
- Verify model files are in the project root directory
- Check file names match exactly
- Ensure files are not corrupted

### Out of Memory
- Close other applications
- Use a machine with at least 8GB RAM
- Consider using a smaller sample for testing

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version` (should be 3.8+)
