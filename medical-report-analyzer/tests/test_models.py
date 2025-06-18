import pytest
from models.disease_classifier import DiseaseClassifier
from models.report_analyzer import ReportAnalyzer
import json
import os
from . import TEST_CONFIG, load_test_data

class TestDiseaseClassifier:
    @pytest.fixture
    def classifier(self):
        return DiseaseClassifier()

    @pytest.fixture
    def sample_text(self):
        return load_test_data('sample_report.txt')

    @pytest.mark.asyncio
    async def test_predict(self, classifier, sample_text):
        predictions = await classifier.predict(sample_text)
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        assert all(
            isinstance(p, dict) and 
            'disease' in p and 
            'confidence' in p 
            for p in predictions
        )

    @pytest.mark.asyncio
    async def test_prediction_confidence(self, classifier, sample_text):
        predictions = await classifier.predict(sample_text)
        for prediction in predictions:
            assert 0 <= prediction['confidence'] <= 1
            assert isinstance(prediction['severity'], str)

class TestReportAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return ReportAnalyzer()

    @pytest.fixture
    def sample_text(self):
        return load_test_data('sample_report.txt')

    @pytest.mark.asyncio
    async def test_analyze_report(self, analyzer, sample_text):
        analysis = await analyzer.analyze_report(sample_text)
        assert isinstance(analysis, dict)
        assert 'entities' in analysis
        assert 'key_findings' in analysis
        assert 'medications' in analysis

    @pytest.mark.asyncio
    async def test_extract_medical_entities(self, analyzer, sample_text):
        entities = await analyzer.extract_medical_entities(sample_text)
        assert isinstance(entities, list)
        assert len(entities) > 0
        assert all(
            isinstance(e, dict) and 
            'text' in e and 
            'type' in e and 
            'confidence' in e 
            for e in entities
        )

    @pytest.mark.asyncio
    async def test_extract_key_findings(self, analyzer, sample_text):
        findings = await analyzer.extract_key_findings(sample_text)
        assert isinstance(findings, list)
        assert len(findings) > 0

    @pytest.mark.asyncio
    async def test_generate_summary(self, analyzer, sample_text):
        summary = await analyzer.generate_summary(sample_text)
        assert isinstance(summary, str)
        assert len(summary) > 0

def test_disease_categories():
    from models import DISEASE_CATEGORIES
    assert isinstance(DISEASE_CATEGORIES, dict)
    assert len(DISEASE_CATEGORIES) > 0
    assert all(
        isinstance(k, int) and 
        isinstance(v, str) 
        for k, v in DISEASE_CATEGORIES.items()
    )

@pytest.mark.parametrize("test_input,expected", [
    ("fever and cough", True),
    ("", False),
    ("normal test results", True)
])
def test_text_validation(test_input, expected):
    classifier = DiseaseClassifier()
    assert classifier.validate_text(test_input) == expected