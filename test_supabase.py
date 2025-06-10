"""
Test script to verify Supabase integration
Run this script to test if Supabase is properly configured
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    try:
        # Import after loading env vars
        from database import DatabaseService
        
        print("🔄 Testing Supabase connection...")
        
        # Test data
        test_prediction = {
            "timestamp": datetime.now().isoformat(),
            "input": {
                "Income": 50000,
                "Age": 30,
                "Dependents": 1,
                "Test": True
            },
            "output": {
                "test_result": "connection_successful",
                "savings_model": {
                    "can_achieve_savings": True,
                    "confidence": 0.95
                }
            }
        }
        
        # Test 1: Create a prediction
        print("📝 Testing prediction creation...")
        result = DatabaseService.create_prediction(test_prediction)
        
        if result:
            prediction_id = result.get('id')
            print(f"✅ Successfully created prediction with ID: {prediction_id}")
            
            # Test 2: Get latest prediction
            print("📖 Testing latest prediction retrieval...")
            latest = DatabaseService.get_latest_prediction()
            
            if latest and latest.get('id') == prediction_id:
                print("✅ Successfully retrieved latest prediction")
                
                # Test 3: Get all predictions
                print("📚 Testing all predictions retrieval...")
                all_predictions = DatabaseService.get_user_predictions()
                
                if all_predictions and len(all_predictions) > 0:
                    print(f"✅ Successfully retrieved {len(all_predictions)} prediction(s)")
                    
                    # Test 4: Delete test prediction
                    print("🗑️ Testing prediction deletion...")
                    deleted = DatabaseService.delete_prediction(prediction_id)
                    
                    if deleted:
                        print("✅ Successfully deleted test prediction")
                        print("\n🎉 All Supabase tests passed!")
                        return True
                    else:
                        print("❌ Failed to delete test prediction")
                else:
                    print("❌ Failed to retrieve predictions")
            else:
                print("❌ Failed to retrieve latest prediction")
        else:
            print("❌ Failed to create prediction")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure Supabase is installed: pip install supabase==2.8.1")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your Supabase configuration in .env file")
    
    return False

def check_environment():
    """Check if environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Main test function"""
    print("🚀 Starting Supabase Integration Test\n")
    
    if not check_environment():
        print("\n💡 To fix this:")
        print("1. Create a .env file in the root directory")
        print("2. Add your Supabase URL and anon key:")
        print("   SUPABASE_URL=https://your-project-id.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key-here")
        sys.exit(1)
    
    print()
    if test_supabase_connection():
        print("\n✨ Supabase integration is working correctly!")
        print("You can now use the application with Supabase database.")
    else:
        print("\n❌ Supabase integration test failed.")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
