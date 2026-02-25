from typing import Optional
from flask import Request


DEMO_USER_ID = 'demo'


def get_user_context(request: Request) -> tuple[Optional[str], bool]:
    user_id = request.headers.get('X-User-ID')
    is_demo = request.headers.get('X-Demo-Mode', 'false').lower() == 'true'

    if is_demo:
        user_id = DEMO_USER_ID

    return user_id, is_demo


def to_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float, returning default on failure."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
