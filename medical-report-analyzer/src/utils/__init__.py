from typing import Dict, Any, List
import yaml
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Utility functions for error handling
def handle_error(error: Exception) -> Dict[str, Any]:
    """Standard error response format"""
    return {
        "success": False,
        "error": str(error),
        "error_type": error.__class__.__name__
    }

# File handling utilities
def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return os.path.splitext(filename)[1].lower()

def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
    """Validate if file size is within limits"""
    return file_size <= max_size

# JSON utilities
def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """Safely load JSON string"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}

def format_response(data: Any, status: bool = True) -> Dict[str, Any]:
    """Standard API response format"""
    return {
        "success": status,
        "data": data,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, None, None, None))
    }
def format_json_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format API response with standard structure"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "success": True,
        "data": data
    }

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    import os
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions

def sanitize_text(text: str) -> str:
    """Clean and sanitize extracted text"""
    import re
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,;:!?()]', '', text)
    return text.strip()

def calculate_confidence_score(predictions: List[Dict]) -> float:
    """Calculate average confidence score"""
    if not predictions:
        return 0.0
    return sum(p.get('confidence', 0) for p in predictions) / len(predictions)

# Export utility functions
__all__ = [
    "handle_error",
    "get_file_extension",
    "validate_file_size",
    "safe_json_loads",
    "format_response",
    "logger"
    "config"
    'format_json_output',
    'validate_file_extension', 
    'sanitize_text',
    'calculate_confidence_score'
]