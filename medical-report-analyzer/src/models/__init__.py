from .disease_classifier import DiseaseClassifier
from .report_analyzer import ReportAnalyzer
from typing import Dict
# Export the model classes
__all__ = [
    "DiseaseClassifier",
    "ReportAnalyzer"
]

# Model configuration
MODEL_CONFIG = {
    "bert_model_name": "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext",
    "max_sequence_length": 512,
    "num_labels":len(DISEASE_CATEGORIES),  # Number of disease categories
    "confidence_threshold": 0.5
}

# Disease categories mapping
DISEASE_CATEGORIES = {
    0: "Cardiovascular",
    1: "Respiratory",
    2: "Gastrointestinal",
    3: "Neurological",
    4: "Musculoskeletal",
    5: "Endocrine",
    6: "Infectious",
    7: "Dermatological",
    8: "Psychological",
    9: "Oncological"
}
# Service configuration  
SERVICE_CONFIG = {
    "document": {
        "supported_formats": [".pdf", ".jpg", ".jpeg", ".png", ".txt"],
        "max_file_size": 10 * 1024 * 1024  # 10MB
    },
    "llm": {
        "model_name": "gpt-3.5-turbo",
        "max_tokens": 500,
        "temperature": 0.7
    }
}

__all__ = ['DISEASE_CATEGORIES', 'MODEL_CONFIG', 'SERVICE_CONFIG']
