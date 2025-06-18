import pytest
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configurations
TEST_CONFIG = {
    "test_data_path": "tests/test_data",
    "sample_reports": {
        "pdf": "sample_report.pdf",
        "image": "sample_report.jpg",
        "text": "sample_report.txt"
    },
    "mock_responses": {
        "llm": "tests/mock_data/llm_responses.json",
        "ocr": "tests/mock_data/ocr_results.json"
    }
}

# Pytest fixtures and configurations
def pytest_configure(config):
    """Configure test environment"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "ocr: mark test as OCR related"
    )
    config.addinivalue_line(
        "markers",
        "llm: mark test as LLM related"
    )

# Common test utilities
def get_test_file_path(filename: str) -> str:
    """Get absolute path for test files"""
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        TEST_CONFIG["test_data_path"],
        filename
    )

def load_test_data(filename: str) -> str:
    """Load test data from file"""
    with open(get_test_file_path(filename), 'r', encoding='utf-8') as f:
        return f.read()

# Export test utilities
__all__ = [
    "TEST_CONFIG",
    "get_test_file_path",
    "load_test_data"
]