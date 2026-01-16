"""
Local-First PII Scrubber (Compliance Layer)
-------------------------------------------
Purpose: Detects and redacts Protected Health Information (PHI/PII) 
locally before data is transmitted to any cloud-based LLM.
"""

import logging
from typing import List, Tuple

# Import Microsoft Presidio libraries
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LocalPIIScrubber:
    """
    Encapsulates the PII scrubbing functionality.
    This class wraps the Presidio analyzer and anonymizer
    to provide a simple interface for scrubbing sensitive data.
    """

    def __init__(self):
        """
        Initializes the local analysis engine.
        Loads the NLP model (spacy) into memory.
        """
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            logging.info("Local PII Scrubber initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Presidio: {e}")
            raise

    def scrub_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Analyzes text for PII and replaces it with generic placeholders.
        
        Args:
            text: The raw input string containing potential PHI.
            
        Returns:
            Tuple containing:
            1. The sanitized text (safe for cloud transmission).
            2. A list of detected entity types (for reporting metrics).
        """
        if not text:
            return "", []

        # 1. Analyze: Find the PII
        # We explicitly look for these entities common in healthcare
        target_entities = [
            "PERSON",           # Patient Names
            "PHONE_NUMBER",     # Contact Info
            "EMAIL_ADDRESS",    # Contact Info
            "US_SSN",           # Social Security
            "US_DRIVER_LICENSE",# ID
            "DATE_TIME"         # Dates (Relevant for HIPAA precision)
        ]

        results = self.analyzer.analyze(
            text=text,
            entities=target_entities,
            language='en'
        )

        # 2. Anonymize: Redact the PII
        # We replace the real data with a placeholder like <PERSON>
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results, # type: ignore
            operators={
                "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
                "PERSON": OperatorConfig("replace", {"new_value": "<PATIENT_NAME>"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"})
            }
        )
        
        # Extract metadata for the PM dashboard (Privacy Metrics)
        detected_types = [res.entity_type for res in results]
        
        return anonymized_result.text, detected_types
