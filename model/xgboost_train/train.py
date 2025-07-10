import numpy as np
import pandas as pd
import json
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

def load_and_preprocess_data():
    """Load and preprocess the financial data"""
    # Load the data
    df = pd.read_csv('data/data.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Handle categorical variables
    categorical_cols = ['Occupation', 'City_Tier']
    label_encoders = {}
    
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le
    
    # Create target variables based on existing data
    df = create_target_variables(df)
    
    return df, label_encoders

def create_target_variables(df):
    """Create target variables for prediction"""
    
    # 1. Can Achieve Savings (Binary: 1 if positive savings potential, 0 otherwise)
    total_potential_savings = df[[col for col in df.columns if 'Potential_Savings' in col]].sum(axis=1)
    df['can_achieve_savings'] = (total_potential_savings > 0).astype(int)
    
    # 2. Savings Confidence (0-100 scale based on income stability and existing savings)
    # Higher confidence for higher income, lower expenses ratio, and existing savings
    expense_ratio = (df['Income'] - df['Disposable_Income']) / df['Income']
    savings_ratio = df['Desired_Savings'] / df['Income']
    
    df['savings_confidence'] = np.clip(
        (1 - expense_ratio) * 50 + savings_ratio * 30 + (df['Income'] / df['Income'].max()) * 20,
        0, 100
    )
    
    # 3. Recommended Savings Amount (combination of desired and potential savings)
    df['recommended_savings_amount'] = np.maximum(
        df['Desired_Savings'], 
        total_potential_savings * 0.8  # 80% of potential savings
    )
    
    # 4. Financial Risk (categorical: Low, Medium, High)
    # Based on debt-to-income ratio, expense ratio, and emergency fund
    debt_to_income = df['Loan_Repayment'] / df['Income']
    emergency_fund_ratio = df['Disposable_Income'] / (df['Income'] * 0.1)  # 10% as baseline
    
    risk_score = debt_to_income * 40 + expense_ratio * 35 + (1/np.maximum(emergency_fund_ratio, 0.1)) * 25
    
    # Create financial risk categories using numpy conditions instead of pd.cut
    # This avoids the categorical data type issue
    conditions = [
        risk_score <= 33,
        (risk_score > 33) & (risk_score <= 66),
        risk_score > 66
    ]
    choices = [0, 1, 2]  # 0=Low, 1=Medium, 2=High
    
    df['financial_risk'] = np.select(conditions, choices, default=-1)  # -1 for NaN/invalid values
    
    # 5. Risk Score (0-100 continuous scale)
    df['risk_score'] = np.clip(risk_score, 0, 100)
    
    return df

def prepare_features(df):
    """Prepare features for training"""
    
    # Define feature columns (exclude target variables and identifier columns)
    feature_cols = [
        'Income', 'Age', 'Dependents', 'Occupation', 'City_Tier',
        'Rent', 'Loan_Repayment', 'Insurance', 'Groceries', 'Transport',
        'Eating_Out', 'Entertainment', 'Utilities', 'Healthcare', 
        'Education', 'Miscellaneous', 'Desired_Savings_Percentage',
        'Disposable_Income'
    ]
    
    # Add potential savings features
    potential_savings_cols = [col for col in df.columns if 'Potential_Savings' in col]
    feature_cols.extend(potential_savings_cols)
    
    # Ensure all feature columns exist
    feature_cols = [col for col in feature_cols if col in df.columns]
    
    X = df[feature_cols].copy()
    
    # Handle missing values
    X = X.fillna(X.median())
    
    # Create additional engineered features
    X['expense_to_income_ratio'] = (X['Income'] - df['Disposable_Income']) / X['Income']
    X['savings_to_income_ratio'] = df['Desired_Savings'] / X['Income']
    X['total_potential_savings'] = df[[col for col in df.columns if 'Potential_Savings' in col]].sum(axis=1)
    X['debt_to_income_ratio'] = X['Loan_Repayment'] / X['Income']
    
    return X, feature_cols

def train_models(X, y_dict):
    """Train XGBoost models for all target variables"""
    
    models = {}
    results = {}
    
    for target_name, y in y_dict.items():
        print(f"\n=== Training model for {target_name} ===")
        
        # Check target variable distribution
        print(f"Target variable distribution for {target_name}:")
        print(y.value_counts().sort_index())
        
        # For classification tasks, use stratified split to ensure both classes are present
        if target_name in ['can_achieve_savings', 'financial_risk']:
            # Check if we have enough samples for each class
            unique_classes = y.unique()
            min_class_count = y.value_counts().min()
            
            if min_class_count < 2:
                print(f"Warning: Not enough samples for stratified split in {target_name}")
                print(f"Minimum class count: {min_class_count}")
                # Use regular split but with different test size
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.1, random_state=42
                )
            else:
                # Use stratified split to maintain class distribution
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
        else:
            # Regular split for regression
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        
        # Determine if classification or regression
        if target_name in ['can_achieve_savings', 'financial_risk']:
            # Classification
            
            # Check if training set has multiple classes
            unique_train_classes = y_train.unique()
            if len(unique_train_classes) < 2:
                print(f"Warning: Training set for {target_name} has only one class: {unique_train_classes}")
                print("Skipping this model...")
                continue
            
            model = xgb.XGBClassifier(
                n_estimators=1000,
                max_depth=15,
                learning_rate=0.1,
                random_state=42,
                eval_metric='logloss'
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Evaluate
            print(f"Classification Report for {target_name}:")
            print(classification_report(y_test, y_pred, zero_division=0))
            
            results[target_name] = {
                'model_type': 'classification',
                'accuracy': (y_test == y_pred).mean(),
                'predictions': y_pred,
                'actual': y_test
            }
            
        else:
            # Regression
            model = xgb.XGBRegressor(
                n_estimators=1000,
                max_depth=15,
                learning_rate=0.1,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Evaluate
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"MSE for {target_name}: {mse:.4f}")
            print(f"R² for {target_name}: {r2:.4f}")
            
            results[target_name] = {
                'model_type': 'regression',
                'mse': mse,
                'r2': r2,
                'predictions': y_pred,
                'actual': y_test
            }
        
        models[target_name] = model
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nTop 10 features for {target_name}:")
        print(feature_importance.head(10))
    
    return models, results

def save_models_and_metadata(models, label_encoders, feature_cols):
    """Save trained models and metadata"""
    
    # Define the base directory
    base_directory = 'model/xgboost_train'
    
    # Ensure the base directory exists
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
    
    # Ensure the trained_model subdirectory exists
    trained_model_dir = os.path.join(base_directory, 'trained_model')
    if not os.path.exists(trained_model_dir):
        os.makedirs(trained_model_dir)
    
    # Save models
    for target_name, model in models.items():
        joblib.dump(model, os.path.join(trained_model_dir, f'xgb_model_{target_name}.pkl'))
    
    # Save label encoders
    joblib.dump(label_encoders, os.path.join(trained_model_dir, 'label_encoders.pkl'))
    
    # Save feature columns
    with open(os.path.join(base_directory, 'feature_columns.json'), 'w') as f:
        json.dump(feature_cols, f)
    
    # Save model metadata
    metadata = {
        'target_variables': list(models.keys()),
        'feature_count': len(feature_cols),
        'model_type': 'XGBoost',
        'description': {
            'can_achieve_savings': 'Binary classification (0: No, 1: Yes)',
            'savings_confidence': 'Regression (0-100 scale)',
            'recommended_savings_amount': 'Regression (currency amount)',
            'financial_risk': 'Classification (0: Low, 1: Medium, 2: High)',
            'risk_score': 'Regression (0-100 scale)'
        }
    }
    
    with open(os.path.join(base_directory, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n=== Models and metadata saved successfully ===")

def create_visualizations(results):
    """Create visualizations for model performance"""
    
    # Define the base directory
    base_directory = 'model/xgboost_train'
    
    # Ensure the img subdirectory exists
    img_dir = os.path.join(base_directory, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.ravel()
    
    for idx, (target_name, result) in enumerate(results.items()):
        if idx >= 6:  # We have 5 targets, so break if more
            break
            
        ax = axes[idx]
        
        if result['model_type'] == 'regression':
            # Scatter plot for regression
            ax.scatter(result['actual'], result['predictions'], alpha=0.6)
            ax.plot([result['actual'].min(), result['actual'].max()], 
                   [result['actual'].min(), result['actual'].max()], 'r--', lw=2)
            ax.set_xlabel('Actual')
            ax.set_ylabel('Predicted')
            ax.set_title(f'{target_name}\nR² = {result["r2"]:.3f}')
        else:
            # Confusion matrix for classification
            from sklearn.metrics import confusion_matrix
            cm = confusion_matrix(result['actual'], result['predictions'])
            sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap='Blues')
            ax.set_title(f'{target_name}\nAccuracy = {result["accuracy"]:.3f}')
    
    # Remove unused subplots
    for idx in range(len(results), 6):
        fig.delaxes(axes[idx])
    
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'model_performance.png'), dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main training pipeline"""
    print("Starting XGBoost training pipeline...")
    
    # Load and preprocess data
    df, label_encoders = load_and_preprocess_data()
    
    # Prepare features
    X, feature_cols = prepare_features(df)
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Features: {X.columns.tolist()}")
    
    # Prepare target variables
    y_dict = {
        'can_achieve_savings': df['can_achieve_savings'],
        'savings_confidence': df['savings_confidence'],
        'recommended_savings_amount': df['recommended_savings_amount'],
        'financial_risk': df['financial_risk'],
        'risk_score': df['risk_score']
    }
    
    # Train models
    models, results = train_models(X, y_dict)
    
    # Save models and metadata
    save_models_and_metadata(models, label_encoders, X.columns.tolist())
    
    # Create visualizations
    create_visualizations(results)
    
    print("\n=== Training completed successfully! ===")
    
    # Print summary
    print("\nModel Summary:")
    for target_name, result in results.items():
        if result['model_type'] == 'regression':
            print(f"- {target_name}: R² = {result['r2']:.3f}")
        else:
            print(f"- {target_name}: Accuracy = {result['accuracy']:.3f}")

if __name__ == "__main__":
    main()