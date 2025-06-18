import pytest
from services.document_processor import DocumentProcessor
from services.llm_service import LLMService
from services.ocr_service import OCRService
import json
import os
from PIL import Image
from . import TEST_CONFIG, load_test_data

class TestDocumentProcessor:
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()

    @pytest.fixture
    def sample_pdf(self):
        with open(os.path.join(TEST_CONFIG["test_data_path"], "sample_report.pdf"), "rb") as f:
            return f.read()

    @pytest.fixture
    def sample_image(self):
        with open(os.path.join(TEST_CONFIG["test_data_path"], "sample_report.jpg"), "rb") as f:
            return f.read()

    @pytest.mark.asyncio
    async def test_process_pdf(self, processor, sample_pdf):
        result = await processor._process_pdf(sample_pdf)
        assert result["success"] is True
        assert "full_text" in result
        assert len(result["full_text"]) > 0

    @pytest.mark.asyncio
    async def test_process_image(self, processor, sample_image):
        result = await processor._process_image(sample_image)
        assert result["success"] is True
        assert "full_text" in result
        assert len(result["full_text"]) > 0

    def test_validate_text(self, processor):
        assert processor.validate_text("Valid medical text") is True
        assert processor.validate_text("") is False

class TestLLMService:
    @pytest.fixture
    def llm_service(self):
        return LLMService()

    @pytest.fixture
    def mock_predictions(self):
        with open(os.path.join(TEST_CONFIG["mock_responses"]["llm"]), 'r') as f:
            return json.load(f)["analysis_responses"][0]["predictions"]

    @pytest.mark.asyncio
    async def test_get_recommendations(self, llm_service):
        text = load_test_data('sample_report.txt')
        recommendations = await llm_service.get_recommendations(
            text, 
            [{"disease": "Respiratory", "confidence": 0.9}]
        )
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(r, dict) for r in recommendations)

    @pytest.mark.asyncio
    async def test_recommendation_structure(self, llm_service):
        text = load_test_data('sample_report.txt')
        recommendations = await llm_service.get_recommendations(
            text,
            [{"disease": "Respiratory", "confidence": 0.9}]
        )
        for rec in recommendations:
            assert "category" in rec
            assert "items" in rec
            assert isinstance(rec["items"], list)

class TestOCRService:
    @pytest.fixture
    def ocr_service(self):
        return OCRService()

    @pytest.fixture
    def sample_image(self):
        image_path = os.path.join(TEST_CONFIG["test_data_path"], "sample_report.jpg")
        return Image.open(image_path)

    @pytest.mark.asyncio
    async def test_extract_text(self, ocr_service, sample_image):
        text = await ocr_service.extract_text(sample_image)
        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_get_confidence_scores(self, ocr_service, sample_image):
        scores = await ocr_service.get_confidence_scores(sample_image)
        assert isinstance(scores, dict)
        assert "average_confidence" in scores
        assert 0 <= scores["average_confidence"] <= 100

    def test_is_image_valid(self, ocr_service, sample_image):
        assert OCRService.is_image_valid(sample_image) is True

@pytest.mark.integration
class TestServiceIntegration:
    @pytest.fixture
    def services(self):
        return {
            "document": DocumentProcessor(),
            "llm": LLMService(),
            "ocr": OCRService()
        }

    @pytest.mark.asyncio
    async def test_end_to_end_processing(self, services):
        # Read sample image
        with open(os.path.join(TEST_CONFIG["test_data_path"], "sample_report.jpg"), "rb") as f:
            image_content = f.read()

        # Process document
        doc_result = await services["document"].process_document(
            image_content, 
            "sample_report.jpg"
        )
        assert doc_result["success"]

        # Get recommendations
        recommendations = await services["llm"].get_recommendations(
            doc_result["full_text"],
            [{"disease": "Respiratory", "confidence": 0.9}]
        )
        assert len(recommendations) > 0