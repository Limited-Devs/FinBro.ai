from flask import Blueprint, request, jsonify
from google import genai
import json
import os
from dotenv import load_dotenv
from database import DatabaseService

load_dotenv()

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env file")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

# Safety settings configuration
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 40,
    "max_output_tokens": 512,
}

# File path for persistent data
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), 'user_data.json')

def read_user_data():
    """Fallback function to read from JSON file"""
    if not os.path.exists(USER_DATA_FILE):
        return {"predictions": []}
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)

def get_latest_prediction():
    """Get latest prediction from Supabase or fallback to JSON"""
    try:
        # Try to get from Supabase first
        latest_prediction = DatabaseService.get_latest_prediction()
        
        if latest_prediction:
            # Transform Supabase data to match expected format
            return {
                "timestamp": latest_prediction["timestamp"],
                "input": latest_prediction["input_data"],
                "output": latest_prediction["output_data"]
            }
        
        # Fallback to JSON file
        data = read_user_data()
        return data["predictions"][-1] if data.get("predictions") else None
        
    except Exception as e:
        print(f"Error getting latest prediction from Supabase: {e}")
        # Fallback to JSON file
        data = read_user_data()
        return data["predictions"][-1] if data.get("predictions") else None

# Create blueprint
chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        latest = get_latest_prediction()

        if not latest:
            return jsonify({
                "response": "I don't have any saved financial data yet. Please make a savings prediction first!"
            })

        input_data = latest.get("input", {})
        output_data = latest.get("output", {})

        # Accessing nested dictionaries safely
        savings_model_output = output_data.get("savings_model", {})
        amount_model_output = output_data.get("amount_model", {})
        multi_task_model_output = output_data.get("multi_task_model", {})

        full_prompt = f"""
You are a Personal Finance Advisor chatbot.
The user recently submitted this financial profile:

Income: ₹{input_data.get("Income", "N/A")}
Age: {input_data.get("Age", "N/A")}
Occupation: {input_data.get("Occupation", "N/A")}
City Tier: {input_data.get("City_Tier", "N/A")}
Dependents: {input_data.get("Dependents", "N/A")}

Monthly Expenses:
Rent: ₹{input_data.get("Rent", "N/A")}
Groceries: ₹{input_data.get("Groceries", "N/A")}
Transport: ₹{input_data.get("Transport", "N/A")}
Eating Out: ₹{input_data.get("Eating_Out", "N/A")}
Utilities: ₹{input_data.get("Utilities", "N/A")}
Healthcare: ₹{input_data.get("Healthcare", "N/A")}
Education: ₹{input_data.get("Education", "N/A")}
Miscellaneous: ₹{input_data.get("Miscellaneous", "N/A")}

Savings Goals:
Desired Savings %: {input_data.get("Desired_Savings_Percentage", "N/A")}%
Disposable Income: ₹{input_data.get("Disposable_Income", "N/A")}
Potential Savings Breakdown:
 - Groceries: ₹{input_data.get("Potential_Savings_Groceries", "N/A")}
 - Transport: ₹{input_data.get("Potential_Savings_Transport", "N/A")}
 - Eating Out: ₹{input_data.get("Potential_Savings_Eating_Out", "N/A")}
 - Utilities: ₹{input_data.get("Potential_Savings_Utilities", "N/A")}
 - Healthcare: ₹{input_data.get("Potential_Savings_Healthcare", "N/A")}
 - Education: ₹{input_data.get("Potential_Savings_Education", "N/A")}
 - Miscellaneous: ₹{input_data.get("Potential_Savings_Miscellaneous", "N/A")}

Prediction Results:
Can Achieve Savings: {'✅ Yes' if savings_model_output.get('can_achieve_savings') else '❌ No'}
Confidence: {savings_model_output.get('confidence', 0) * 100:.2f}%
Recommended Monthly Savings: ₹{amount_model_output.get('recommended_savings', 0):,.2f}
Financial Risk: {'⚠️ Yes' if multi_task_model_output.get('financial_risk') else '✅ No'}

Now the user is asking:
"{user_message}"

Instructions:
- For greetings/casual talk: Respond naturally and friendly
- For finance questions: Use their data to give personalized advice
- For general questions: Answer normally without forcing financial data
- Keep all responses under 100 words and conversational
- Always give response in plain text, do not use any ** or formatting
"""

        # Generate content using the client (simplified approach)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        
        return jsonify({"response": response.text})

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500