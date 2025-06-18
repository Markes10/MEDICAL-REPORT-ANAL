import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
from typing import Dict, Any
from .ocr_service import OCRService
from .. import SERVICE_CONFIG

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = SERVICE_CONFIG["document"]["supported_formats"]
        self.max_file_size = SERVICE_CONFIG["document"]["max_file_size"]
        self.ocr_service = OCRService()

    async def process_document(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """
        Process uploaded medical document and extract text
        """
        # Validate file
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        if len(file_content) > self.max_file_size:
            raise ValueError(f"File size exceeds maximum limit of {self.max_file_size/1024/1024}MB")

        # Process based on file type
        if file_ext == '.pdf':
            return await self._process_pdf(file_content)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return await self._process_image(file_content)
        elif file_ext == '.txt':
            return await self._process_text(file_content)
        
    async def _process_pdf(self, content: bytes) -> Dict[str, Any]:
        """Process PDF documents"""
        try:
            pages = convert_from_bytes(content)
            text_content = ""
            page_texts = []

            for i, page in enumerate(pages):
                page_text = await self.ocr_service.extract_text(page)
                page_texts.append({
                    "page_number": i + 1,
                    "content": page_text
                })
                text_content += f"\n=== Page {i+1} ===\n{page_text}"

            return {
                "success": True,
                "full_text": text_content.strip(),
                "pages": page_texts,
                "page_count": len(pages)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF processing failed: {str(e)}"
            }

    async def _process_image(self, content: bytes) -> Dict[str, Any]:
        """Process image documents"""
        try:
            image = Image.open(io.BytesIO(content))
            text = await self.ocr_service.extract_text(image)
            
            return {
                "success": True,
                "full_text": text.strip(),
                "pages": [{
                    "page_number": 1,
                    "content": text
                }],
                "page_count": 1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Image processing failed: {str(e)}"
            }

    async def _process_text(self, content: bytes) -> Dict[str, Any]:
        """Process text documents"""
        try:
            text = content.decode('utf-8')
            return {
                "success": True,
                "full_text": text.strip(),
                "pages": [{
                    "page_number": 1,
                    "content": text
                }],
                "page_count": 1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Text processing failed: {str(e)}"
            }

    def validate_text(self, text: str) -> bool:
        """
        Validate extracted text for quality and content
        """
        if not text or len(text.strip()) < 10:
            return False
            
        # Check for common OCR errors or garbage text
        error_indicators = ['�', '□', '■', '¤']
        error_count = sum(text.count(indicator) for indicator in error_indicators)
        
        return error_count / len(text) < 0.1