from fastapi import APIRouter, UploadFile, File, HTTPException
from services.document_processor import DocumentProcessor
from models.disease_classifier import DiseaseClassifier
from services.llm_service import LLMService
import os

router = APIRouter()
doc_processor = DocumentProcessor()
disease_classifier = DiseaseClassifier()
llm_service = LLMService()

@router.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    """
    Analyze medical report and return predictions and recommendations
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Read and process file
        content = await file.read()
        
        # Extract text from document
        text = await doc_processor.extract_text(content, file_ext)
        
        # Get disease predictions
        predictions = await disease_classifier.predict(text)
        
        # Get medical recommendations
        recommendations = await llm_service.get_recommendations(text, predictions)
        
        return {
            "status": "success",
            "text": text,
            "predictions": predictions,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats
    """
    return {
        "formats": [
            "PDF (.pdf)",
            "Images (.png, .jpg, .jpeg)",
            "Text (.txt)"
        ]
    }