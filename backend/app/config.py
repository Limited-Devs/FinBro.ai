"""
Environment-based configuration for FinBro.ai backend.

Supports:
- DevelopmentConfig: Debug mode, verbose logging
- ProductionConfig: Optimized for deployment
- TestingConfig: For automated tests
"""
import os
from datetime import timedelta
from typing import List


class BaseConfig:
    """Base configuration shared across all environments."""
    
    # Flask
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR: str = os.path.join(os.path.dirname(BASE_DIR), 'model')
    FEATURE_INFO_FILE: str = os.path.join(MODEL_DIR, 'feature_info.json')
    
    # Supabase
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_ANON_KEY', '')
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = 'gemini-2.0-flash'
    GEMINI_MAX_TOKENS: int = 512
    GEMINI_TEMPERATURE: float = 0.7
    
    # CORS
    CORS_ORIGINS: List[str] = ['http://localhost:5173', 'http://localhost:5000']
    
    # Rate Limiting
    RATELIMIT_ENABLED: bool = True
    RATELIMIT_DEFAULT: str = '100 per minute'
    RATELIMIT_STORAGE_URL: str = 'memory://'
    RATELIMIT_STRATEGY: str = 'fixed-window'
    
    # Prediction-specific limits
    PREDICT_RATE_LIMIT: str = '10 per minute'
    CHAT_RATE_LIMIT: str = '30 per minute'
    
    # Caching
    CACHE_TYPE: str = 'simple'
    CACHE_DEFAULT_TIMEOUT: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = 'json'  # 'json' or 'text'
    
    # Feature Flags
    ENABLE_PREDICTION_CACHE: bool = True
    ENABLE_JSON_FALLBACK: bool = True  # Fallback to JSON file if Supabase fails


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    DEBUG: bool = True
    TESTING: bool = False
    LOG_LEVEL: str = 'DEBUG'
    LOG_FORMAT: str = 'text'
    
    # More lenient rate limits for development
    RATELIMIT_ENABLED: bool = False
    PREDICT_RATE_LIMIT: str = '100 per minute'
    CHAT_RATE_LIMIT: str = '100 per minute'


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = 'WARNING'
    
    # Strict rate limits for production
    RATELIMIT_ENABLED: bool = True
    PREDICT_RATE_LIMIT: str = '10 per minute'
    CHAT_RATE_LIMIT: str = '30 per minute'
    
    # Production security
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    DEBUG: bool = True
    TESTING: bool = True
    LOG_LEVEL: str = 'DEBUG'
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED: bool = False
    
    # Disable caching for tests
    CACHE_TYPE: str = 'null'
    ENABLE_PREDICTION_CACHE: bool = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)
