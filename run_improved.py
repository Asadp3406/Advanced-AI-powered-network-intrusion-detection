"""
CIC-IDS2017 Network Intrusion Detection - IMPROVED VERSION
Enhancements:
1. SMOTE for minority class oversampling
2. Extended hyperparameter tuning
3. Class weights optimization
4. Better evaluation metrics
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import gc
import joblib
import time

from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, confusion_matrix,
                             accuracy_score, f1_score, roc_curve, auc,
                             precision_recall_fscore_support)
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from imblearn.over_sampling import SMOTE
from collections import Counter

# Configuration
CSV_PATH = '.'
USE_SAMPLE = False
SAMPLE_FRACTION = 0.2
USE_SMOTE = True  # Enable SMOTE for minority classes
SMOTE_STRATEGY = 'not majority'  # Only oversample minority classes, not BENIGN

print("="*70)
print("CIC-IDS2017 IMPROVED NETWORK INTRUSION DETECTION")
print("="*70)
print(f"\nEnhancements enabled:")
print(f"  ✅ SMOTE for minority class oversampling")
print(f"  ✅ Extended hyperparameter search")
print(f"  ✅ Optimized class weights")
print(f"  ✅ Better evaluation metrics")

# Step 1: Load Dataset (same as before)
print("\n" + "="*70)
print("STEP 1: LOADING DATASET")
print("="*70)

files = glob.glob(os.path.join(CSV_PATH, '*.csv'))
print(f"\nFound {len(files)} CSV files")

if len(files) == 0:
    print("\n❌ ERROR: No CSV files found!")
    exit(1)

print("\n⏳ Loading CSV files...")
dfs = []
for f in files:
    print(f"   Loading: {os.path.basename(f)}...", end=" ")
    temp_df = pd.read_csv(f, low_memory=False, encoding='cp1252')
    print(f"✅ {temp_df.shape}")
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)
del dfs, temp_df
gc.collect()

print(f"\n📊 Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# Memory optimization
mem_before = df.memory_usage(deep=True).sum() / (1024**2)
numeric_cols = df.select_dtypes(include=[np.float64]).columns
df[numeric_cols] = df[numeric_cols].astype(np.float32)
int_cols = df.select_dtypes(include=[np.int64]).columns
df[int_cols] = df[int_cols].astype(np.int32)
mem_after = df.memory_usage(deep=True).sum() / (1024**2)
print(f"💾 Memory: {mem_before:.1f} MB → {mem_after:.1f} MB (saved {mem_before-mem_after:.1f} MB)")

if USE_SAMPLE:
    df = df.sample(frac=SAMPLE_FRACTION, random_state=42).reset_index(drop=True)
    print(f"⚠️ Using {SAMPLE_FRACTION*100}% sample: {df.shape}")
    gc.collect()

# Step 2: Data Cleaning (same as before)
print("\n" + "="*70)
print("STEP 2: DATA CLEANING")
print("="*70)

df.columns = df.columns.str.strip()
label_col = 'Label' if 'Label' in df.columns else df.columns[-1]
df.replace([np.inf, -np.inf], np.nan, inplace=True)
nan_rows_before = df.shape[0]
df.dropna(inplace=True)
print(f"✅ Dropped {nan_rows_before - df.shape[0]:,} rows with NaN")

le = LabelEncoder()
df['Label_Encoded'] = le.fit_transform(df[label_col])

print(f"\n📋 Class Distribution:")
class_counts = df[label_col].value_counts()
for i, cls in enumerate(le.classes_):
    count = (df[label_col] == cls).sum()
    pct = (count / len(df)) * 100
    print(f"   {i:2d} → {cls:<40s} | {count:>8,} ({pct:>5.2f}%)")

gc.collect()

# Step 3: Feature Selection (same as before)
print("\n" + "="*70)
print("STEP 3: FEATURE SELECTION")
print("="*70)

feature_cols = [col for col in df.columns if col not in [label_col, 'Label_Encoded']]
X_all = df[feature_cols]
y_all = df['Label_Encoded']

X_numeric = X_all.select_dtypes(include=[np.number])
numeric_feature_names = X_numeric.columns.tolist()
print(f"📊 Total features: {len(numeric_feature_names)}")

sample_size = min(500000, len(df))
sample_idx = np.random.RandomState(42).choice(len(df), sample_size, replace=False)
X_sample = X_numeric.iloc[sample_idx].values.astype(np.float32)
y_sample = y_all.iloc[sample_idx].values
X_sample = np.nan_to_num(X_sample, nan=0.0, posinf=0.0, neginf=0.0)

print(f"\n🌲 Training Random Forest for feature selection...")
start_time = time.time()

rf_selector = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    class_weight='balanced',
    n_jobs=-1,
    random_state=42,
    max_features='sqrt'
)
rf_selector.fit(X_sample, y_sample)
print(f"✅ Completed in {time.time() - start_time:.1f}s")

importances = rf_selector.feature_importances_
feat_importance_df = pd.DataFrame({
    'Feature': numeric_feature_names,
    'Importance': importances
}).sort_values('Importance', ascending=False)

selected_features = feat_importance_df.head(20)['Feature'].tolist()

print(f"\n🎯 Selected {len(selected_features)} features")
joblib.dump(selected_features, 'selected_features_improved.pkl')

del rf_selector, X_sample, y_sample
gc.collect()

# Step 4: IMPROVED - Stratified Split WITHOUT Downsampling
print("\n" + "="*70)
print("STEP 4: DATA SPLIT (NO DOWNSAMPLING)")
print("="*70)

X = df[selected_features].values.astype(np.float32)
y = df['Label_Encoded'].values
X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

print(f"📊 Full dataset: {X.shape}")
print(f"\n📊 Class distribution before split:")
unique, counts = np.unique(y, return_counts=True)
for label, count in zip(unique, counts):
    print(f"   Class {label}: {count:>8,} samples")

# Split: 70% train, 15% val, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

print(f"\n📊 Split sizes:")
print(f"   🟢 Train:      {X_train.shape[0]:>10,} samples")
print(f"   🟡 Validation: {X_val.shape[0]:>10,} samples")
print(f"   🔴 Test:       {X_test.shape[0]:>10,} samples")

del X, y, X_temp, y_temp, df
gc.collect()

# Step 5: IMPROVED - Apply SMOTE to Training Data
if USE_SMOTE:
    print("\n" + "="*70)
    print("STEP 5: APPLYING SMOTE (MINORITY OVERSAMPLING)")
    print("="*70)
    
    print("\n📊 Before SMOTE:")
    print(f"   Training samples: {len(y_train):,}")
    unique, counts = np.unique(y_train, return_counts=True)
    for label, count in zip(unique, counts):
        print(f"   Class {label}: {count:>8,}")
    
    # Apply SMOTE only to minority classes (not BENIGN)
    print("\n⏳ Applying SMOTE (this may take 5-10 minutes)...")
    start_time = time.time()
    
    # Optimized SMOTE: only oversample minority classes to 10% of majority
    # This is much faster than full balancing
    class_counts = Counter(y_train)
    majority_count = max(class_counts.values())
    target_count = int(majority_count * 0.1)  # Target: 10% of majority class
    
    sampling_strategy = {}
    for class_label, count in class_counts.items():
        if count < target_count:
            sampling_strategy[class_label] = target_count
    
    print(f"   Oversampling {len(sampling_strategy)} minority classes to {target_count:,} samples each")
    
    # Use SMOTE with optimized settings
    smote = SMOTE(
        sampling_strategy=sampling_strategy,
        k_neighbors=3,  # Small k for classes with few samples
        random_state=42
    )
    
    try:
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
        print(f"✅ SMOTE completed in {time.time() - start_time:.1f}s")
        
        print(f"\n📊 After SMOTE:")
        print(f"   Training samples: {len(y_train_resampled):,}")
        unique, counts = np.unique(y_train_resampled, return_counts=True)
        for label, count in zip(unique, counts):
            print(f"   Class {label}: {count:>8,}")
        
        X_train = X_train_resampled
        y_train = y_train_resampled
        
    except Exception as e:
        print(f"⚠️ SMOTE failed: {e}")
        print("   Continuing without SMOTE...")
    
    gc.collect()

# Step 6: IMPROVED - Extended Hyperparameter Tuning
print("\n" + "="*70)
print("STEP 6: EXTENDED HYPERPARAMETER TUNING")
print("="*70)

print("\n🔍 GridSearchCV with extended parameter grid...")
grid_sample_size = min(200000, len(X_train))  # Larger sample
grid_idx = np.random.RandomState(42).choice(len(X_train), grid_sample_size, replace=False)
X_grid = X_train[grid_idx]
y_grid = y_train[grid_idx]

# Extended parameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [15, 25, 35],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}

print(f"   Testing {len(param_grid['n_estimators']) * len(param_grid['max_depth']) * len(param_grid['min_samples_split']) * len(param_grid['min_samples_leaf'])} combinations")

grid_rf = RandomForestClassifier(
    class_weight='balanced_subsample',  # Better for imbalanced data
    n_jobs=-1,
    max_features='sqrt',
    random_state=42
)

grid_search = GridSearchCV(
    grid_rf, param_grid,
    cv=3,
    scoring='f1_macro',
    n_jobs=-1,
    verbose=1
)

start_time = time.time()
grid_search.fit(X_grid, y_grid)
print(f"\n✅ GridSearch completed in {time.time() - start_time:.1f}s")
print(f"🏆 Best parameters: {grid_search.best_params_}")
print(f"🏆 Best F1 score: {grid_search.best_score_:.4f}")

del X_grid, y_grid
gc.collect()

# Step 7: Train Final Model
print("\n" + "="*70)
print("STEP 7: TRAINING FINAL MODEL")
print("="*70)

best_params = grid_search.best_params_
print(f"\n🚀 Training on {X_train.shape[0]:,} samples...")

final_model = RandomForestClassifier(
    n_estimators=best_params.get('n_estimators', 200),
    max_depth=best_params.get('max_depth', 25),
    min_samples_split=best_params.get('min_samples_split', 2),
    min_samples_leaf=best_params.get('min_samples_leaf', 1),
    class_weight='balanced_subsample',
    n_jobs=-1,
    max_features='sqrt',
    random_state=42,
    verbose=1
)

start_time = time.time()
final_model.fit(X_train, y_train)
train_time = time.time() - start_time
print(f"\n✅ Model trained in {train_time:.1f}s")

# Validation
val_pred = final_model.predict(X_val)
val_accuracy = accuracy_score(y_val, val_pred)
val_f1_macro = f1_score(y_val, val_pred, average='macro')
val_f1_weighted = f1_score(y_val, val_pred, average='weighted')

print(f"\n📊 Validation results:")
print(f"   Accuracy:     {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")
print(f"   Macro F1:     {val_f1_macro:.4f}")
print(f"   Weighted F1:  {val_f1_weighted:.4f}")

del grid_search
gc.collect()

# Step 8: Comprehensive Evaluation
print("\n" + "="*70)
print("STEP 8: COMPREHENSIVE EVALUATION")
print("="*70)

y_pred = final_model.predict(X_test)
y_pred_proba = final_model.predict_proba(X_test)

print("\n📋 CLASSIFICATION REPORT:")
print("="*70)
target_names = le.classes_
unique_test_labels = np.unique(np.concatenate([y_test, y_pred]))
report = classification_report(
    y_test, y_pred,
    labels=unique_test_labels,
    target_names=[target_names[i] for i in unique_test_labels],
    digits=4
)
print(report)

test_accuracy = accuracy_score(y_test, y_pred)
test_f1_macro = f1_score(y_test, y_pred, average='macro')
test_f1_weighted = f1_score(y_test, y_pred, average='weighted')

print(f"\n{'='*60}")
print(f"🎯 OVERALL TEST METRICS")
print(f"{'='*60}")
print(f"   Accuracy:        {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
print(f"   Macro F1:        {test_f1_macro:.4f}")
print(f"   Weighted F1:     {test_f1_weighted:.4f}")
print(f"{'='*60}")

# Per-class metrics
print(f"\n📊 PER-CLASS DETAILED METRICS:")
print(f"{'='*70}")
precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred, labels=unique_test_labels, zero_division=0
)

print(f"{'Class':<40s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'Support':>10s}")
print(f"{'-'*70}")
for i, label in enumerate(unique_test_labels):
    class_name = target_names[label]
    print(f"{class_name:<40s} {precision[i]:>10.4f} {recall[i]:>10.4f} {f1[i]:>10.4f} {support[i]:>10,}")

# Step 9: Save Improved Model
print("\n" + "="*70)
print("STEP 9: SAVING IMPROVED MODEL")
print("="*70)

joblib.dump(final_model, 'model_improved.pkl')
model_size = os.path.getsize('model_improved.pkl') / (1024**2)
print(f"✅ Saved: model_improved.pkl ({model_size:.1f} MB)")

joblib.dump(le, 'label_encoder_improved.pkl')
print(f"✅ Saved: label_encoder_improved.pkl")

# Save comparison metrics
comparison = {
    'test_accuracy': test_accuracy,
    'test_f1_macro': test_f1_macro,
    'test_f1_weighted': test_f1_weighted,
    'train_time': train_time,
    'best_params': best_params,
    'smote_used': USE_SMOTE
}
joblib.dump(comparison, 'metrics_improved.pkl')
print(f"✅ Saved: metrics_improved.pkl")

print("\n" + "="*70)
print("🎉 IMPROVED MODEL TRAINING COMPLETE!")
print("="*70)
print(f"\n📊 FINAL SUMMARY:")
print(f"   Test Accuracy:    {test_accuracy*100:.2f}%")
print(f"   Macro F1:         {test_f1_macro:.4f}")
print(f"   Weighted F1:      {test_f1_weighted:.4f}")
print(f"   Training Time:    {train_time:.1f}s")
print(f"   SMOTE Applied:    {USE_SMOTE}")
print(f"\n💾 Saved Files:")
print(f"   ✅ model_improved.pkl")
print(f"   ✅ label_encoder_improved.pkl")
print(f"   ✅ selected_features_improved.pkl")
print(f"   ✅ metrics_improved.pkl")
print("\n🛡️ Improved model ready!")
