from .document_processor import DocumentProcessor
from .llm_service import LLMService
from .ocr_service import OCRService

# Export service classes
__all__ = [
    "DocumentProcessor",
    "LLMService",
    "OCRService"
]

# Service configuration
SERVICE_CONFIG = {
    "ocr": {
        "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        "lang": "eng",
        "config": "--psm 3"
    },
    "llm": {
        "model_name": "gpt-3.5-turbo",
        "max_tokens": 500,
        "temperature": 0.7
    },
    "document": {
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "supported_formats": ['.pdf', '.png', '.jpg', '.jpeg', '.txt']
    }
}

# Constants for service operations
ANALYSIS_TYPES = {
    "BASIC": "basic_analysis",
    "DETAILED": "detailed_analysis",
    "EMERGENCY": "emergency_analysis"
}