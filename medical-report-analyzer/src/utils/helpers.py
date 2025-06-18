from typing import Dict, Any, List, Optional
import datetime
import re
import hashlib
import json

def sanitize_text(text: str) -> str:
    """Remove special characters and normalize text"""
    # Remove special characters but keep medical symbols
    text = re.sub(r'[^\w\s+°−–%/]', '', text)
    # Normalize whitespace
    return ' '.join(text.split())

def parse_date(date_str: str) -> Optional[datetime.datetime]:
    """Parse different date formats commonly found in medical reports"""
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def extract_measurements(text: str) -> List[Dict[str, Any]]:
    """Extract medical measurements with units"""
    measurements = []
    
    # Common medical measurements patterns
    patterns = {
        'blood_pressure': r'(\d{2,3})/(\d{2,3})\s*(?:mmHg)?',
        'temperature': r'(\d{2,3}(?:\.\d)?)\s*[°℃℉]',
        'weight': r'(\d{2,3}(?:\.\d)?)\s*(?:kg|lbs)',
        'height': r'(\d{2,3}(?:\.\d)?)\s*(?:cm|m|ft)'
    }
    
    for measure_type, pattern in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            measurements.append({
                'type': measure_type,
                'value': match.group(1),
                'raw_text': match.group(0)
            })
    
    return measurements

def generate_report_id(content: str) -> str:
    """Generate unique report ID based on content"""
    return hashlib.md5(content.encode()).hexdigest()

def format_medical_terms(terms: List[str]) -> List[Dict[str, str]]:
    """Format medical terms with their categories"""
    formatted_terms = []
    for term in terms:
        category = classify_medical_term(term)
        formatted_terms.append({
            'term': term,
            'category': category
        })
    return formatted_terms

def classify_medical_term(term: str) -> str:
    """Classify medical term into categories"""
    categories = {
        'diagnosis': ['syndrome', 'disease', 'disorder', 'condition'],
        'medication': ['tablet', 'capsule', 'injection', 'mg', 'ml'],
        'test': ['test', 'scan', 'xray', 'mri', 'ct', 'level'],
        'symptom': ['pain', 'ache', 'discomfort', 'feeling']
    }
    
    term_lower = term.lower()
    for category, keywords in categories.items():
        if any(keyword in term_lower for keyword in keywords):
            return category
    return 'other'

def validate_medical_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate medical report data"""
    required_fields = ['patient_id', 'report_date', 'content']
    validation_result = {
        'is_valid': True,
        'missing_fields': [],
        'errors': []
    }
    
    for field in required_fields:
        if field not in report_data:
            validation_result['is_valid'] = False
            validation_result['missing_fields'].append(field)
    
    if 'report_date' in report_data:
        try:
            parse_date(report_data['report_date'])
        except ValueError:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Invalid date format')
    
    return validation_result

def anonymize_patient_data(text: str) -> str:
    """Remove or mask sensitive patient information"""
    # Mask common patterns for sensitive data
    patterns = {
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b'
    }
    
    anonymized_text = text
    for pattern_type, pattern in patterns.items():
        anonymized_text = re.sub(pattern, f'[REDACTED {pattern_type}]', anonymized_text)
    
    return anonymized_text

def format_json_output(data: Dict[str, Any]) -> str:
    """Format dictionary as pretty JSON string"""
    return json.dumps(data, indent=2, ensure_ascii=False)