"""
Prediction repository for data access.

Provides clean interface for prediction CRUD operations
with Supabase as primary storage and JSON file fallback.
"""
import os
import json
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client

from app.models.exceptions import DatabaseError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PredictionRepository:
    """
    Repository for prediction data access.
    
    Implements the repository pattern with:
    - Supabase as primary storage
    - JSON file fallback for resilience
    - Clean interface hiding storage details
    """
    
    _supabase_client: Optional[Client] = None
    _file_lock = threading.Lock()
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None,
                 fallback_file: str = None, enable_fallback: bool = True):
        """
        Initialize the repository.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
            fallback_file: Path to JSON fallback file
            enable_fallback: Whether to use JSON fallback
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        self.fallback_file = fallback_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'user_data.json'
        )
        self.enable_fallback = enable_fallback
        
        self._init_supabase()
    
    def _init_supabase(self) -> None:
        """Initialize Supabase client if credentials available."""
        if self.supabase_url and self.supabase_key:
            try:
                self._supabase_client = create_client(
                    self.supabase_url, 
                    self.supabase_key
                )
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase: {e}")
                self._supabase_client = None
        else:
            logger.warning("Supabase credentials not configured")
    
    @property
    def supabase(self) -> Optional[Client]:
        """Get Supabase client."""
        return self._supabase_client
    
    def create(self, input_data: Dict[str, Any], output_data: Dict[str, Any],
               user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new prediction record.
        
        Args:
            input_data: Financial input data
            output_data: ML model predictions
            user_id: Optional user ID
        
        Returns:
            Created record with ID, or None on failure
        """
        timestamp = datetime.now().isoformat()
        
        if self.supabase:
            try:
                record = self._create_supabase_record(
                    input_data, output_data, timestamp, user_id
                )
                if record:
                    logger.info(f"Created prediction in Supabase: {record.get('id')}")
                    return record
            except Exception as e:
                logger.error(f"Supabase create failed: {e}")
        
        # Fallback to JSON
        if self.enable_fallback:
            return self._create_json_record(input_data, output_data, timestamp)
        
        raise DatabaseError("Failed to create prediction", operation="create")
    
    def _create_supabase_record(
        self, 
        input_data: Dict[str, Any], 
        output_data: Dict[str, Any],
        timestamp: str,
        user_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Create record in Supabase."""
        data = self._build_supabase_data(input_data, output_data, timestamp, user_id)
        result = self.supabase.table("predictions").insert(data).execute()
        return result.data[0] if result.data else None
    
    def _build_supabase_data(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        timestamp: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Build Supabase record from input/output data."""
        # Extract model outputs safely
        savings_model = output_data.get("savings_model", {})
        amount_model = output_data.get("amount_model", {})
        multi_task = output_data.get("multi_task_model", {})
        
        return {
            "timestamp": timestamp,
            "user_id": user_id,
            
            # Basic financial info
            "income": float(input_data.get("Income", 0)),
            "age": int(input_data.get("Age", 0)),
            "dependents": int(input_data.get("Dependents", 0)),
            "occupation": input_data.get("Occupation"),
            "city_tier": input_data.get("City_Tier"),
            
            # Expenses
            "rent": float(input_data.get("Rent", 0)),
            "loan_repayment": float(input_data.get("Loan_Repayment", 0)),
            "insurance": float(input_data.get("Insurance", 0)),
            "groceries": float(input_data.get("Groceries", 0)),
            "transport": float(input_data.get("Transport", 0)),
            "eating_out": float(input_data.get("Eating_Out", 0)),
            "entertainment": float(input_data.get("Entertainment", 0)),
            "utilities": float(input_data.get("Utilities", 0)),
            "healthcare": float(input_data.get("Healthcare", 0)),
            "education": float(input_data.get("Education", 0)),
            "miscellaneous": float(input_data.get("Miscellaneous", 0)),
            
            # Savings info
            "desired_savings_percentage": float(input_data.get("Desired_Savings_Percentage", 0)),
            "disposable_income": float(input_data.get("Disposable_Income", 0)),
            
            # Potential savings
            "potential_savings_groceries": float(input_data.get("Potential_Savings_Groceries", 0)),
            "potential_savings_transport": float(input_data.get("Potential_Savings_Transport", 0)),
            "potential_savings_eating_out": float(input_data.get("Potential_Savings_Eating_Out", 0)),
            "potential_savings_entertainment": float(input_data.get("Potential_Savings_Entertainment", 0)),
            "potential_savings_utilities": float(input_data.get("Potential_Savings_Utilities", 0)),
            "potential_savings_healthcare": float(input_data.get("Potential_Savings_Healthcare", 0)),
            "potential_savings_education": float(input_data.get("Potential_Savings_Education", 0)),
            "potential_savings_miscellaneous": float(input_data.get("Potential_Savings_Miscellaneous", 0)),
            
            # ML predictions
            "savings_model_can_achieve": savings_model.get("can_achieve_savings"),
            "savings_model_confidence": float(savings_model.get("confidence", 0)),
            "amount_model_recommended_savings": float(amount_model.get("recommended_savings", 0)),
            "multi_task_can_achieve": multi_task.get("can_achieve_savings"),
            "multi_task_savings_confidence": float(multi_task.get("savings_confidence", 0)),
            "multi_task_recommended_amount": float(multi_task.get("recommended_savings_amount", 0)),
            "multi_task_financial_risk": multi_task.get("financial_risk"),
            "multi_task_risk_score": float(multi_task.get("risk_score", 0))
        }
    
    def _create_json_record(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        timestamp: str
    ) -> Dict[str, Any]:
        """Create record in JSON fallback file."""
        record = {
            "timestamp": timestamp,
            "input": input_data,
            "output": output_data
        }
        
        def _save():
            try:
                with self._file_lock:
                    data = {"predictions": [record]}
                    with open(self.fallback_file, 'w') as f:
                        json.dump(data, f, indent=2)
                logger.info("Saved prediction to JSON fallback")
            except Exception as e:
                logger.error(f"JSON fallback failed: {e}")
        
        # Save in background
        threading.Thread(target=_save, daemon=True).start()
        return record
    
    def get_all(
        self, 
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all predictions with optional filtering and pagination.
        
        Args:
            user_id: Filter by user ID (optional)
            limit: Maximum records to return
            offset: Number of records to skip
        
        Returns:
            List of prediction records
        """
        if self.supabase:
            try:
                return self._get_from_supabase(user_id, limit, offset)
            except Exception as e:
                logger.error(f"Supabase fetch failed: {e}")
        
        # Fallback to JSON
        if self.enable_fallback:
            return self._get_from_json()
        
        return []
    
    def _get_from_supabase(
        self,
        user_id: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Fetch predictions from Supabase."""
        query = (
            self.supabase.table("predictions")
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .offset(offset)
        )
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        result = query.execute()
        return [self._format_supabase_record(r) for r in result.data]
    
    def _format_supabase_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Format Supabase record to standard structure."""
        return {
            "id": record["id"],
            "timestamp": record["timestamp"],
            "input_data": {
                "Income": record["income"],
                "Age": record["age"],
                "Dependents": record["dependents"],
                "Occupation": record["occupation"],
                "City_Tier": record["city_tier"],
                "Rent": record["rent"],
                "Loan_Repayment": record["loan_repayment"],
                "Insurance": record["insurance"],
                "Groceries": record["groceries"],
                "Transport": record["transport"],
                "Eating_Out": record["eating_out"],
                "Entertainment": record["entertainment"],
                "Utilities": record["utilities"],
                "Healthcare": record["healthcare"],
                "Education": record["education"],
                "Miscellaneous": record["miscellaneous"],
                "Desired_Savings_Percentage": record["desired_savings_percentage"],
                "Disposable_Income": record["disposable_income"],
                "Potential_Savings_Groceries": record["potential_savings_groceries"],
                "Potential_Savings_Transport": record["potential_savings_transport"],
                "Potential_Savings_Eating_Out": record["potential_savings_eating_out"],
                "Potential_Savings_Entertainment": record["potential_savings_entertainment"],
                "Potential_Savings_Utilities": record["potential_savings_utilities"],
                "Potential_Savings_Healthcare": record["potential_savings_healthcare"],
                "Potential_Savings_Education": record["potential_savings_education"],
                "Potential_Savings_Miscellaneous": record["potential_savings_miscellaneous"],
            },
            "output_data": {
                "savings_model": {
                    "can_achieve_savings": record["savings_model_can_achieve"],
                    "confidence": record["savings_model_confidence"]
                },
                "amount_model": {
                    "recommended_savings": record["amount_model_recommended_savings"]
                },
                "multi_task_model": {
                    "can_achieve_savings": record["multi_task_can_achieve"],
                    "savings_confidence": record["multi_task_savings_confidence"],
                    "recommended_savings_amount": record["multi_task_recommended_amount"],
                    "financial_risk": record["multi_task_financial_risk"],
                    "risk_score": record["multi_task_risk_score"]
                }
            }
        }
    
    def _get_from_json(self) -> List[Dict[str, Any]]:
        """Fetch predictions from JSON fallback."""
        try:
            if os.path.exists(self.fallback_file):
                with open(self.fallback_file, 'r') as f:
                    data = json.load(f)
                    predictions = data.get("predictions", [])
                    # Format to match Supabase structure
                    return [{
                        "timestamp": p["timestamp"],
                        "input_data": p["input"],
                        "output_data": p["output"]
                    } for p in predictions]
        except Exception as e:
            logger.error(f"JSON read failed: {e}")
        return []
    
    def get_latest(self, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the most recent prediction.
        
        Args:
            user_id: Filter by user ID (optional)
        
        Returns:
            Latest prediction or None
        """
        predictions = self.get_all(user_id=user_id, limit=1)
        return predictions[0] if predictions else None
    
    def delete(self, prediction_id: str) -> bool:
        """
        Delete a prediction by ID.
        
        Args:
            prediction_id: The prediction ID to delete
        
        Returns:
            True if deleted, False otherwise
        """
        if not self.supabase:
            return False
        
        try:
            self.supabase.table("predictions").delete().eq("id", prediction_id).execute()
            logger.info(f"Deleted prediction: {prediction_id}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check repository health.
        
        Returns:
            Health status dictionary
        """
        status = {
            "supabase": "unhealthy",
            "json_fallback": "unhealthy"
        }
        
        # Check Supabase
        if self.supabase:
            try:
                self.supabase.table("predictions").select("id").limit(1).execute()
                status["supabase"] = "healthy"
            except Exception:
                pass
        
        # Check JSON fallback
        if self.enable_fallback:
            try:
                fallback_dir = os.path.dirname(self.fallback_file)
                if os.path.exists(fallback_dir) and os.access(fallback_dir, os.W_OK):
                    status["json_fallback"] = "healthy"
            except Exception:
                pass
        
        return status
