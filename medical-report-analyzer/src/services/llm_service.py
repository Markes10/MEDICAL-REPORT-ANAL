from typing import List, Dict, Any
import openai
from transformers import pipeline
import os
from .. import SERVICE_CONFIG

class LLMService:
    def __init__(self):
        self.model_name = SERVICE_CONFIG["llm"]["model_name"]
        self.max_tokens = SERVICE_CONFIG["llm"]["max_tokens"]
        self.temperature = SERVICE_CONFIG["llm"]["temperature"]
        
        # Initialize OpenAI if API key is available
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            
        # Fallback to local model if no API key
        self.local_pipeline = pipeline(
            "text-generation",
            model="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
        )

    async def get_recommendations(self, text: str, predictions: List[Dict]) -> Dict[str, Any]:
        """
        Generate medical recommendations based on report text and predictions
        """
        try:
            if self.openai_api_key:
                return await self._get_openai_recommendations(text, predictions)
            else:
                return await self._get_local_recommendations(text, predictions)
        except Exception as e:
            return {
                "error": f"Failed to generate recommendations: {str(e)}",
                "recommendations": []
            }

    async def _get_openai_recommendations(self, text: str, predictions: List[Dict]) -> Dict[str, Any]:
        """Generate recommendations using OpenAI"""
        prompt = self._create_prompt(text, predictions)
        
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a medical assistant providing recommendations based on medical reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return {
            "recommendations": self._parse_recommendations(response.choices[0].message.content),
            "model_used": "openai"
        }

    async def _get_local_recommendations(self, text: str, predictions: List[Dict]) -> Dict[str, Any]:
        """Generate recommendations using local model"""
        prompt = self._create_prompt(text, predictions)
        
        result = self.local_pipeline(
            prompt,
            max_length=self.max_tokens,
            num_return_sequences=1
        )
        
        return {
            "recommendations": self._parse_recommendations(result[0]['generated_text']),
            "model_used": "local"
        }

    def _create_prompt(self, text: str, predictions: List[Dict]) -> str:
        """Create prompt for recommendation generation"""
        diseases = ", ".join([p["disease"] for p in predictions])
        return f"""
        Based on the medical report and predicted conditions: {diseases}
        
        Medical Report Text:
        {text[:1000]}...  # Truncate for length
        
        Please provide:
        1. Key medical recommendations
        2. Suggested follow-up tests
        3. Lifestyle modifications
        4. Potential medication considerations (general classes only)
        5. Warning signs to watch for
        """

    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        """Parse and structure the model's response"""
        categories = {
            "Medical": [],
            "Tests": [],
            "Lifestyle": [],
            "Medications": [],
            "Warnings": []
        }
        
        current_category = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if "recommendation" in line.lower():
                current_category = "Medical"
            elif "test" in line.lower():
                current_category = "Tests"
            elif "lifestyle" in line.lower():
                current_category = "Lifestyle"
            elif "medication" in line.lower():
                current_category = "Medications"
            elif "warning" in line.lower():
                current_category = "Warnings"
            elif current_category and line.startswith('- '):
                categories[current_category].append(line[2:])

        return [
            {"category": k, "items": v}
            for k, v in categories.items()
            if v
        ]