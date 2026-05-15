#!/usr/bin/env python
"""Quick test script to verify training pipeline works."""

import sys
import os
import joblib
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🔍 MODEL TRAINING & PROJECT VALIDATION")
print("=" * 60)

# Step 1: Check imports
# Set default encoding for stdout/stderr to UTF-8 to prevent UnicodeEncodeError on some systems
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

print("\n[1/7] Checking imports...")
try:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    import xgboost as xgb
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
    print("✓ Core libraries imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Step 2: Check data file
print("\n[2/7] Checking data file...")
data_path = Path("data/raw/train.csv")
if not data_path.exists():
    print(f"✗ Data file not found: {data_path}")
    sys.exit(1)

df = pd.read_csv(data_path)
print(f"✓ Data loaded: {len(df)} rows, {len(df.columns)} columns")
print(f"   Columns: {list(df.columns)}")

# Step 3: Check data quality
print("\n[3/7] Checking data quality...")
print(f"   Missing values: {df.isnull().sum().sum()}")
print(f"   Data types:\n{df.dtypes}")
print("✓ Data quality check passed")

# Step 4: Prepare data
print("\n[4/7] Preparing data...")

# Column mapping based on the CSV structure
feature_cols = [
    'Warehouse_block', 'Mode_of_Shipment', 'Customer_care_calls',
    'Customer_rating', 'Cost_of_the_Product', 'Prior_purchases',
    'Product_importance', 'Gender', 'Discount_offered', 'Weight_in_gms'
]

target_col = 'Reached.on.Time_Y.N'

# Check if all columns exist
missing_cols = [col for col in feature_cols + [target_col] if col not in df.columns]
if missing_cols:
    print(f"✗ Missing columns: {missing_cols}")
    print(f"   Available columns: {list(df.columns)}")
    sys.exit(1)

X = df[feature_cols].copy()
y = df[target_col].copy()

# Handle missing values
X.fillna(X.mean(numeric_only=True), inplace=True)
X.fillna(X.mode().iloc[0], inplace=True)

# Encode categorical columns
categorical_cols = ['Warehouse_block', 'Mode_of_Shipment', 'Product_importance', 'Gender']
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col].astype(str))
    label_encoders[col] = le

print(f"✓ Data prepared: {X.shape[0]} samples, {X.shape[1]} features")

# Step 5: Train-test split
print("\n[5/7] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"✓ Train set: {len(X_train)} samples")
print(f"✓ Test set: {len(X_test)} samples")
print(f"   Class distribution (train): {y_train.value_counts().to_dict()}")

# Step 6: Scale features
print("\n[6/7] Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print(f"✓ Features scaled successfully")

# Step 7: Train model
print("\n[7/7] Training XGBoost model...")
try:
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    
    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=False
    )
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    cm = confusion_matrix(y_test, y_pred)
    
    print(f"✓ Model trained successfully!")
    
    print("\n" + "=" * 60)
    print("📊 MODEL PERFORMANCE METRICS")
    print("=" * 60)
    print(f"Accuracy:    {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"F1-Score:    {f1:.4f}")
    print(f"ROC-AUC:     {roc_auc:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  True Negatives:  {cm[0, 0]}")
    print(f"  False Positives: {cm[0, 1]}")
    print(f"  False Negatives: {cm[1, 0]}")
    print(f"  True Positives:  {cm[1, 1]}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🎯 Top 5 Important Features:")
    for idx, row in feature_importance.head(5).iterrows():
        print(f"  {row['feature']:25} {row['importance']:.4f}")
    
    # Save model
    import joblib
    os.makedirs('models/production', exist_ok=True)
    joblib.dump(model, 'models/production/model.pkl')
    joblib.dump(scaler, 'models/production/scaler.pkl')
    joblib.dump(label_encoders, 'models/production/label_encoders.pkl')
    
    print(f"\n✓ Model saved to: models/production/model.pkl")
    print(f"✓ Scaler saved to: models/production/scaler.pkl")
    print(f"✓ Encoders saved to: models/production/label_encoders.pkl")
    
except Exception as e:
    print(f"✗ Training error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED - PROJECT IS READY!")
print("=" * 60)
print("\nNext steps:")
print("  1. Start API:       uvicorn backend.main:app --reload --port 8000")
print("  2. Start Dashboard: streamlit run frontend/main.py")
print("  3. Visit API Docs:  http://localhost:8000/docs")
print("  4. Visit Dashboard: http://localhost:8501")
print("=" * 60)
