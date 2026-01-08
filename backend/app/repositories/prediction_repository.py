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
        # Database schema uses jsonb for input_data and output_data
        return {
            "timestamp": timestamp,
            "user_id": user_id,
            "input_data": input_data,
            "output_data": output_data
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
        # Unpack JSONB fields
        input_data = record.get("input_data", {})
        output_data = record.get("output_data", {})
        
        return {
            "id": record["id"],
            "timestamp": record["timestamp"],
            "input_data": {
                "Income": input_data.get("Income"),
                "Age": input_data.get("Age"),
                "Dependents": input_data.get("Dependents"),
                "Occupation": input_data.get("Occupation"),
                "City_Tier": input_data.get("City_Tier"),
                "Rent": input_data.get("Rent"),
                "Loan_Repayment": input_data.get("Loan_Repayment"),
                "Insurance": input_data.get("Insurance"),
                "Groceries": input_data.get("Groceries"),
                "Transport": input_data.get("Transport"),
                "Eating_Out": input_data.get("Eating_Out"),
                "Entertainment": input_data.get("Entertainment"),
                "Utilities": input_data.get("Utilities"),
                "Healthcare": input_data.get("Healthcare"),
                "Education": input_data.get("Education"),
                "Miscellaneous": input_data.get("Miscellaneous"),
                "Desired_Savings_Percentage": input_data.get("Desired_Savings_Percentage"),
                "Disposable_Income": input_data.get("Disposable_Income"),
                "Potential_Savings_Groceries": input_data.get("Potential_Savings_Groceries"),
                "Potential_Savings_Transport": input_data.get("Potential_Savings_Transport"),
                "Potential_Savings_Eating_Out": input_data.get("Potential_Savings_Eating_Out"),
                "Potential_Savings_Entertainment": input_data.get("Potential_Savings_Entertainment"),
                "Potential_Savings_Utilities": input_data.get("Potential_Savings_Utilities"),
                "Potential_Savings_Healthcare": input_data.get("Potential_Savings_Healthcare"),
                "Potential_Savings_Education": input_data.get("Potential_Savings_Education"),
                "Potential_Savings_Miscellaneous": input_data.get("Potential_Savings_Miscellaneous"),
            },
            "output_data": {
                "savings_model": output_data.get("savings_model", {}),
                "amount_model": output_data.get("amount_model", {}),
                "multi_task_model": output_data.get("multi_task_model", {})
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
    
    def get_monthly_trends(
        self,
        user_id: Optional[str] = None,
        months: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated monthly financial data for trend visualization.
        
        Args:
            user_id: Filter by user ID (optional)
            months: Number of months of history to return
        
        Returns:
            List of monthly aggregated data sorted by date
        """
        # Get recent predictions
        predictions = self.get_all(user_id=user_id, limit=months * 5)  # Extra buffer for multiple per month
        
        if not predictions:
            return []
        
        # Group by month
        monthly_data: Dict[str, Dict[str, Any]] = {}
        
        for pred in predictions:
            try:
                timestamp = pred.get("timestamp", "")
                if not timestamp:
                    continue
                    
                # Parse timestamp and get month key
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                month_key = dt.strftime("%Y-%m")
                month_name = dt.strftime("%b")
                
                input_data = pred.get("input_data", {})
                output_data = pred.get("output_data", {})
                
                # Use latest prediction for each month
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "month": month_name,
                        "month_key": month_key,
                        "income": input_data.get("Income", 0) or 0,
                        "expenses": sum([
                            input_data.get("Rent", 0) or 0,
                            input_data.get("Groceries", 0) or 0,
                            input_data.get("Utilities", 0) or 0,
                            input_data.get("Transport", 0) or 0,
                            input_data.get("Insurance", 0) or 0,
                            input_data.get("Eating_Out", 0) or 0,
                            input_data.get("Healthcare", 0) or 0,
                            input_data.get("Entertainment", 0) or 0,
                            input_data.get("Miscellaneous", 0) or 0,
                        ]),
                        "actual_savings": input_data.get("Disposable_Income", 0) or 0,
                        "target_savings": output_data.get("amount_model", {}).get("recommended_savings", 0) or 0
                    }
            except Exception as e:
                logger.warning(f"Error processing prediction for trends: {e}")
                continue
        
        # Sort by month_key and return last N months
        sorted_months = sorted(monthly_data.values(), key=lambda x: x["month_key"])
        return sorted_months[-months:]

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
