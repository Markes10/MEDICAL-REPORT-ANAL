import pytesseract
from PIL import Image
import numpy as np
from typing import Union, Dict, Any
import cv2
import os

class OCRService:
    def __init__(self):
        # Set Tesseract path from environment or default to 'tesseract'
        tesseract_path = os.getenv("TESSERACT_PATH", "tesseract")
        if tesseract_path != "tesseract":
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Default OCR configurations
        self.lang = os.getenv("OCR_LANG", "eng")
        self.config = os.getenv("OCR_CONFIG", "--psm 3 --oem 3")

    async def extract_text(self, image: Union[Image.Image, np.ndarray]) -> str:
        """
        Extract text from image using OCR.
        Supports both PIL Image and numpy ndarray formats.
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)

            # Preprocess image for better OCR results
            processed_image = await self._preprocess_image(image)

            text = pytesseract.image_to_string(
                processed_image,
                lang=self.lang,
                config=self.config
            )
            return text.strip()
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to enhance OCR accuracy.
        Steps: grayscale -> threshold -> dilation -> noise reduction
        """
        img_array = np.array(image)

        # Convert to grayscale if image is colored
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply thresholding and morphological operations
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        gray = cv2.dilate(gray, kernel, iterations=1)
        gray = cv2.medianBlur(gray, 3)

        return Image.fromarray(gray)

    async def get_confidence_scores(self, image: Union[Image.Image, np.ndarray]) -> Dict[str, Any]:
        """
        Get OCR confidence scores for the given image.
        Returns average, min, max confidence, and word count.
        """
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)

            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            confidences = [int(conf) for conf in data['conf'] if conf != '-1' and int(conf) > 0]

            if confidences:
                return {
                    "average_confidence": sum(confidences) / len(confidences),
                    "min_confidence": min(confidences),
                    "max_confidence": max(confidences),
                    "word_count": len(confidences)
                }
            else:
                return {"average_confidence": 0, "min_confidence": 0, "max_confidence": 0, "word_count": 0}

        except Exception as e:
            return {"error": f"Confidence score calculation failed: {str(e)}"}

    @staticmethod
    async def is_image_valid(image: Union[Image.Image, np.ndarray]) -> bool:
        """
        Validate whether the image is suitable for OCR.
        Checks size and variance to ensure content.
        """
        try:
            if isinstance(image, np.ndarray):
                img_array = image
                height, width = img_array.shape[:2]
            else:
                img_array = np.array(image)
                width, height = image.size

            min_dimension = 100
            min_pixels = 10000

            # Check size and if image content is not uniform (to filter blanks)
            return (
                width >= min_dimension and
                height >= min_dimension and
                (width * height) >= min_pixels and
                img_array.std() > 10
            )
        except Exception:
            return False
