"""
Pydantic schemas for request/response validation.

Provides:
- Input validation with meaningful error messages
- Type coercion for API inputs
- Response serialization
"""
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class Occupation(str, Enum):
    """Valid occupation types."""
    SALARIED = "Salaried"
    SELF_EMPLOYED = "Self_Employed"
    STUDENT = "Student"
    RETIRED = "Retired"


class CityTier(str, Enum):
    """Valid city tier types."""
    TIER_1 = "Tier_1"
    TIER_2 = "Tier_2"
    TIER_3 = "Tier_3"


# ============================================================================
# Prediction Schemas
# ============================================================================

class PredictionRequest(BaseModel):
    """Schema for financial prediction request."""
    
    # Basic info
    Income: float = Field(..., gt=0, description="Monthly income (must be positive)")
    Age: int = Field(..., ge=18, le=100, description="Age (18-100)")
    Dependents: int = Field(..., ge=0, le=20, description="Number of dependents")
    Occupation: str = Field(..., description="Occupation type")
    City_Tier: str = Field(..., description="City tier classification")
    
    # Monthly expenses
    Rent: float = Field(..., ge=0, description="Monthly rent")
    Loan_Repayment: float = Field(..., ge=0, description="Monthly loan repayment")
    Insurance: float = Field(..., ge=0, description="Monthly insurance")
    Groceries: float = Field(..., ge=0, description="Monthly groceries")
    Transport: float = Field(..., ge=0, description="Monthly transport")
    Eating_Out: float = Field(..., ge=0, description="Monthly eating out")
    Entertainment: float = Field(..., ge=0, description="Monthly entertainment")
    Utilities: float = Field(..., ge=0, description="Monthly utilities")
    Healthcare: float = Field(..., ge=0, description="Monthly healthcare")
    Education: float = Field(..., ge=0, description="Monthly education")
    Miscellaneous: float = Field(..., ge=0, description="Monthly miscellaneous")
    
    # Savings goals
    Desired_Savings_Percentage: float = Field(..., ge=0, le=100, description="Desired savings percentage (0-100)")
    Disposable_Income: float = Field(..., ge=0, description="Monthly disposable income")
    
    # Potential savings
    Potential_Savings_Groceries: float = Field(..., ge=0)
    Potential_Savings_Transport: float = Field(..., ge=0)
    Potential_Savings_Eating_Out: float = Field(..., ge=0)
    Potential_Savings_Entertainment: float = Field(..., ge=0)
    Potential_Savings_Utilities: float = Field(..., ge=0)
    Potential_Savings_Healthcare: float = Field(..., ge=0)
    Potential_Savings_Education: float = Field(..., ge=0)
    Potential_Savings_Miscellaneous: float = Field(..., ge=0)
    
    @field_validator('Occupation')
    @classmethod
    def validate_occupation(cls, v: str) -> str:
        valid = ['Salaried', 'Self_Employed', 'Student', 'Retired']
        if v not in valid:
            raise ValueError(f"Occupation must be one of: {', '.join(valid)}")
        return v
    
    @field_validator('City_Tier')
    @classmethod
    def validate_city_tier(cls, v: str) -> str:
        valid = ['Tier_1', 'Tier_2', 'Tier_3']
        if v not in valid:
            raise ValueError(f"City_Tier must be one of: {', '.join(valid)}")
        return v
    
    @model_validator(mode='after')
    def validate_expenses(self) -> 'PredictionRequest':
        """Validate that expenses don't exceed income."""
        total_expenses = (
            self.Rent + self.Loan_Repayment + self.Insurance +
            self.Groceries + self.Transport + self.Eating_Out +
            self.Entertainment + self.Utilities + self.Healthcare +
            self.Education + self.Miscellaneous
        )
        if total_expenses > self.Income * 2:
            raise ValueError("Total expenses seem unusually high compared to income")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "Income": 50000,
                "Age": 30,
                "Dependents": 2,
                "Occupation": "Salaried",
                "City_Tier": "Tier_1",
                "Rent": 15000,
                "Loan_Repayment": 5000,
                "Insurance": 2000,
                "Groceries": 8000,
                "Transport": 3000,
                "Eating_Out": 2000,
                "Entertainment": 1500,
                "Utilities": 2500,
                "Healthcare": 1000,
                "Education": 0,
                "Miscellaneous": 1000,
                "Desired_Savings_Percentage": 20,
                "Disposable_Income": 9000,
                "Potential_Savings_Groceries": 1000,
                "Potential_Savings_Transport": 500,
                "Potential_Savings_Eating_Out": 1000,
                "Potential_Savings_Entertainment": 500,
                "Potential_Savings_Utilities": 300,
                "Potential_Savings_Healthcare": 200,
                "Potential_Savings_Education": 0,
                "Potential_Savings_Miscellaneous": 500
            }
        }


class SavingsModelResult(BaseModel):
    """Result from the savings achievement model."""
    can_achieve_savings: bool
    confidence: float = Field(..., ge=0, le=1)


class AmountModelResult(BaseModel):
    """Result from the savings amount model."""
    recommended_savings: float


class MultiTaskModelResult(BaseModel):
    """Result from the multi-task model."""
    can_achieve_savings: bool
    savings_confidence: float = Field(..., ge=0, le=1)
    recommended_savings_amount: float
    financial_risk: bool
    risk_score: float = Field(..., ge=0, le=1)


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    savings_model: SavingsModelResult
    amount_model: AmountModelResult
    multi_task_model: MultiTaskModelResult


# ============================================================================
# Chat Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        return v


class ChatResponse(BaseModel):
    """Schema for chat response."""
    response: str


# ============================================================================
# Health Check Schemas
# ============================================================================

class ComponentHealth(BaseModel):
    """Health status of a single component."""
    status: Literal["healthy", "degraded", "unhealthy"]
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str = "1.0.0"
    environment: str
    components: Dict[str, ComponentHealth]
    uptime_seconds: Optional[float] = None


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorDetail(BaseModel):
    """Schema for error details."""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: bool = True
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
