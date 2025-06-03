from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import tensorflow as tf
import json
import os
from datetime import datetime
import threading
import warnings
# Import chatbot blueprint
from chatBot import chat_bp as chat_app
# Import database service
from database import DatabaseService

# Initialize Flask app with static folder pointing to React build
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=UserWarning, module='keras')

# Paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
FEATURE_INFO_FILE = os.path.join(MODEL_DIR, 'feature_info.json')
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), 'user_data.json')

# Load feature info
with open(FEATURE_INFO_FILE, 'r') as f:
    feature_info = json.load(f)

FEATURE_ORDER = feature_info['numerical_features'] + feature_info['categorical_features']
TOTAL_FEATURES = len(FEATURE_ORDER)

# Load models once
models = {}
for name in ['savings', 'amount', 'multi_task']:
    models[name] = tf.keras.models.load_model(
        os.path.join(MODEL_DIR, f'trained_model/best_{name}_model.keras'), compile=False)

# Thread lock for file operations
file_lock = threading.Lock()

def save_user_data(input_data, output_data):
    """Save user input and output to Supabase database"""
    try:
        prediction_data = {
            "timestamp": datetime.now().isoformat(),
            "input": input_data,
            "output": output_data
        }
        
        # Save to Supabase
        result = DatabaseService.create_prediction(prediction_data)
        
        if result:
            print(f"Data saved to Supabase successfully with ID: {result.get('id')}")
        else:
            print("Failed to save data to Supabase")
            # Fallback to JSON file if Supabase fails
            save_user_data_json(input_data, output_data)
            
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        # Fallback to JSON file if Supabase fails
        save_user_data_json(input_data, output_data)

def save_user_data_json(input_data, output_data):
    """Fallback: Save user input and output to JSON file"""
    def _save():
        try:
            with file_lock:
                # Create new data structure with only the current entry
                data = {
                    "predictions": [{
                        "timestamp": datetime.now().isoformat(),
                        "input": input_data,
                        "output": output_data
                    }]
                }
                
                # Save to file, overwriting any existing content
                with open(USER_DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    # Run in background thread
    threading.Thread(target=_save, daemon=True).start()

def process_features(data):
    """Process input data into feature vector"""
    # Extract and convert all inputs
    base_data = {
        "Income": float(data["Income"]),
        "Age": int(data["Age"]),
        "Dependents": int(data["Dependents"]),
        "Desired_Savings_Percentage": float(data["Desired_Savings_Percentage"]),
        "Disposable_Income": float(data["Disposable_Income"])
    }
    
    # Expenses and potential savings
    expense_keys = ["Rent", "Loan_Repayment", "Insurance", "Groceries", "Transport",
                   "Eating_Out", "Entertainment", "Utilities", "Healthcare", "Education", "Miscellaneous"]
    potential_keys = [f"Potential_Savings_{k}" for k in ["Groceries", "Transport", "Eating_Out", 
                     "Entertainment", "Utilities", "Healthcare", "Education", "Miscellaneous"]]
    
    expenses = {k: float(data[k]) for k in expense_keys}
    potential_savings = {k: float(data[k]) for k in potential_keys}
    
    # Compute derived features
    total_expenses = sum(expenses.values())
    essential_expenses = sum(expenses[k] for k in ["Rent", "Loan_Repayment", "Groceries", "Transport", "Utilities", "Healthcare"])
    actual_savings_potential = sum(potential_savings.values())
    
    # Build feature dictionary
    features = {
        **base_data,
        **expenses,
        **potential_savings,
        "Savings_Rate": base_data["Desired_Savings_Percentage"] / 100,
        "Actual_Savings_Potential": actual_savings_potential,
        "Essential_Expenses": essential_expenses,
        "Essential_Expense_Ratio": essential_expenses / base_data["Income"],
        "Non_Essential_Income": base_data["Income"] - essential_expenses,
        "Expense_Efficiency": actual_savings_potential / base_data["Disposable_Income"] if base_data["Disposable_Income"] > 0 else 0,
        "Total_Expenses": total_expenses,
        "Debt_to_Income_Ratio": expenses["Loan_Repayment"] / base_data["Income"],
        "Financial_Stress_Score": 1 - (base_data["Disposable_Income"] / base_data["Income"]),
        
        # Categorical features (one-hot encoding)
        "Occupation_Retired": int(data["Occupation"] == "Retired"),
        "Occupation_Self_Employed": int(data["Occupation"] == "Self_Employed"),
        "Occupation_Student": int(data["Occupation"] == "Student"),
        "City_Tier_Tier_2": int(data["City_Tier"] == "Tier_2"),
        "City_Tier_Tier_3": int(data["City_Tier"] == "Tier_3"),
        "Age_Group_Young_Adult": int(base_data["Age"] < 25),
        "Age_Group_Mid_Career": int(25 <= base_data["Age"] < 40),
        "Age_Group_Pre_Retirement": int(40 <= base_data["Age"] < 60),
        "Age_Group_Senior": int(base_data["Age"] >= 60),
        "Income_Bracket_Low_Income": int(base_data["Income"] < 20000),
        "Income_Bracket_Lower_Mid": int(20000 <= base_data["Income"] < 40000),
        "Income_Bracket_Middle": int(40000 <= base_data["Income"] < 70000),
        "Income_Bracket_Upper_Mid": int(base_data["Income"] >= 70000),
        "Savings_Difficulty_Moderate": 0,
        "Savings_Difficulty_Very_Hard": 0,
        "Savings_Difficulty_nan": 1
    }
    
    return np.array([features[name] for name in FEATURE_ORDER], dtype=np.float32).reshape(1, -1)

# API Routes
@app.route('/api/')
def home():
    return jsonify({"message": "Savings Prediction API", "features": TOTAL_FEATURES, "status": "running"})

# Register the chat blueprint under /api/chat
app.register_blueprint(chat_app, url_prefix='/api/chat')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Process features
        X = process_features(data)
        
        # Get predictions with suppressed warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            predictions = {name: model.predict(X, verbose=0) for name, model in models.items()}
        
        # Format results
        result = {
            "savings_model": {
                "can_achieve_savings": bool(predictions['savings'][0][0] > 0.5),
                "confidence": float(predictions['savings'][0][0])
            },
            "amount_model": {
                "recommended_savings": float(predictions['amount'][0][0])
            },
            "multi_task_model": {
                "can_achieve_savings": bool(predictions['multi_task'][0][0][0] > 0.5),
                "savings_confidence": float(predictions['multi_task'][0][0][0]),
                "recommended_savings_amount": float(predictions['multi_task'][1][0][0]),
                "financial_risk": bool(predictions['multi_task'][2][0][0] > 0.5),
                "risk_score": float(predictions['multi_task'][2][0][0])
            }
        }
        
        # Save data in background
        save_user_data(data, result)
        
        return jsonify(result)
        
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "models": len(models), "features": TOTAL_FEATURES})

@app.route('/api/data', methods=['GET'])
def get_user_data():
    """Get saved user data from Supabase or fallback to JSON"""
    try:
        # Try to get data from Supabase first
        predictions = DatabaseService.get_user_predictions()
        
        if predictions:
            # Transform Supabase data to match expected format
            formatted_predictions = []
            for pred in predictions:
                formatted_predictions.append({
                    "timestamp": pred["timestamp"],
                    "input": pred["input_data"],
                    "output": pred["output_data"]
                })
            
            return jsonify({
                "total_predictions": len(formatted_predictions),
                "predictions": formatted_predictions
            })
        
        # Fallback to JSON file if Supabase is empty or fails
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
                return jsonify({
                    "total_predictions": len(data.get("predictions", [])),
                    "predictions": data.get("predictions", [])
                })
        
        return jsonify({"total_predictions": 0, "predictions": []})
        
    except Exception as e:
        print(f"Error in get_user_data: {e}")
        # Fallback to JSON file on any error
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r') as f:
                    data = json.load(f)
                    return jsonify({
                        "total_predictions": len(data.get("predictions", [])),
                        "predictions": data.get("predictions", [])
                    })
        except Exception as json_error:
            print(f"JSON fallback also failed: {json_error}")
        
        return jsonify({"error": f"Failed to load data: {str(e)}"}), 500

# Serve React App
@app.route('/')
def serve_react():
    """Serve the main React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_or_react(path):
    """Serve static files or React app for client-side routing"""
    try:
        # Try to serve static file first
        return send_from_directory(app.static_folder, path)
    except:
        # If file doesn't exist, serve React app (for client-side routing)
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)