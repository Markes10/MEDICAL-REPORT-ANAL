from typing import List, Dict, Any
import re
from transformers import pipeline

class ReportAnalyzer:
    def __init__(self):
        # Initialize NER pipelines for flexibility
        self.ner_pipeline_biobert = pipeline("ner", model="dmis-lab/biobert-v1.1")
        self.ner_pipeline_biomedical = pipeline(
            "ner",
            model="d4data/biomedical-ner-all",
            tokenizer="d4data/biomedical-ner-all",
            aggregation_strategy="simple"
        )
        self.qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
        self.summary_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

    async def analyze_report(self, text: str) -> Dict[str, Any]:
        try:
            entities = await self.extract_medical_entities(text)
            key_findings = await self.extract_key_findings(text)
            medications = await self.extract_medications(text)
            recommended_tests = await self.extract_recommended_tests(text)
            summary = await self.generate_summary(text)
            severity = await self.get_severity_indicators(entities)

            return {
                "entities": entities,
                "key_findings": key_findings,
                "recommended_tests": recommended_tests,
                "medications": medications,
                "summary": summary,
                "severity": severity
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    async def extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        try:
            entities = self.ner_pipeline_biomedical(text)
            results = []
            for entity in entities:
                results.append({
                    "text": entity.get("word", entity.get("token", "")),
                    "type": entity.get("entity_group", entity.get("entity", "")),
                    "confidence": entity.get("score", 0),
                    "start": entity.get("start", None),
                    "end": entity.get("end", None)
                })
            return results
        except Exception:
            return []

    async def extract_key_findings(self, text: str) -> List[str]:
        questions = [
            "What are the main symptoms?",
            "What are the diagnostic findings?",
            "What are the abnormal results?"
        ]
        findings = []
        try:
            for question in questions:
                result = self.qa_pipeline(question=question, context=text)
                if result['score'] > 0.7:
                    findings.append(result['answer'])
            return findings
        except Exception:
            return findings

    async def extract_recommended_tests(self, text: str) -> List[str]:
        question = "What medical tests are recommended?"
        try:
            result = self.qa_pipeline(question=question, context=text)
            if result['score'] > 0.7:
                tests = [test.strip() for test in result['answer'].split(',')]
                return [test for test in tests if len(test) > 2]
            return []
        except Exception:
            return []

    async def extract_medications(self, text: str) -> List[str]:
        med_patterns = [
            r"\b\w+cillin\b",  # Antibiotics
            r"\b\w+statin\b",  # Statins
            r"\b(?:ibuprofen|aspirin|metformin|insulin)\b"
        ]
        medications = []
        try:
            for pattern in med_patterns:
                medications.extend(re.findall(pattern, text, re.IGNORECASE))
            return list(set(medications))
        except Exception:
            return []

    async def generate_summary(self, text: str, max_length: int = 150) -> str:
        try:
            summary = self.summary_pipeline(text, max_length=max_length, min_length=50, do_sample=False)[0]['summary_text']
            return summary
        except Exception:
            # Fallback to extractive summary if transformer fails
            sentences = text.split('.')
            keywords = ['diagnosis', 'treatment', 'recommendation', 'finding', 'result']
            important = [s.strip() for s in sentences if any(k in s.lower() for k in keywords)]
            return '. '.join(important[:3]) + '.' if important else text[:200] + '...'

    async def get_severity_indicators(self, entities: List[Dict]) -> str:
        severity_keywords = {
            "high": ["severe", "critical", "urgent", "emergency"],
            "medium": ["moderate", "concerning", "significant"],
            "low": ["mild", "minor", "slight"]
        }
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for entity in entities:
            text = entity['text'].lower()
            for level, keywords in severity_keywords.items():
                if any(keyword in text for keyword in keywords):
                    severity_counts[level] += 1
        if severity_counts["high"] > 0:
            return "high"
        elif severity_counts["medium"] > 0:
            return "medium"
        else:
            return "low"
