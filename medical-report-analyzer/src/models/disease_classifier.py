from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Tuple
import numpy as np
from . import MODEL_CONFIG, DISEASE_CATEGORIES

class DiseaseClassifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_CONFIG["bert_model_name"])
        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_CONFIG["bert_model_name"],
            num_labels=MODEL_CONFIG["num_labels"]
        ).to(self.device)
        self.confidence_threshold = MODEL_CONFIG["confidence_threshold"]

    async def preprocess_text(self, text: str) -> Dict:
        """Tokenize and prepare text for model input"""
        return self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=MODEL_CONFIG["max_sequence_length"],
            return_tensors="pt"
        )

    async def predict(self, text: str) -> List[Dict]:
        """
        Predict diseases from medical report text
        Returns list of predictions with confidence scores
        """
        # Preprocess text
        inputs = await self.preprocess_text(text)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.sigmoid(outputs.logits).squeeze().cpu().numpy()

        # Format predictions
        predictions = []
        for idx, prob in enumerate(probabilities):
            if prob >= self.confidence_threshold:
                predictions.append({
                    "disease": DISEASE_CATEGORIES[idx],
                    "confidence": float(prob),
                    "severity": await self._calculate_severity(prob)
                })

        return sorted(predictions, key=lambda x: x["confidence"], reverse=True)

    async def _calculate_severity(self, probability: float) -> str:
        """Calculate severity level based on confidence score"""
        if probability >= 0.8:
            return "High"
        elif probability >= 0.6:
            return "Medium"
        else:
            return "Low"

    async def get_symptoms(self, text: str) -> List[str]:
        """Extract relevant symptoms from text using BERT"""
        # TODO: Implement symptom extraction using BERT
        return []

    @staticmethod
    def get_disease_categories() -> Dict[int, str]:
        """Return available disease categories"""
        return DISEASE_CATEGORIES