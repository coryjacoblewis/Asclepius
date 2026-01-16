"""
Asclepius: Main Orchestrator (Secure Gateway)
---------------------------------------------
Purpose: Coordinates the workflow between the Local PII Scrubber and the 
Cloud-based Clinical Evaluator. Enforces the security boundary.
"""

import logging
import json
from scrubber import LocalPIIScrubber
from evaluator import ClinicalEvaluator

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [ORCHESTRATOR] - %(levelname)s - %(message)s'
)

class HealthAIGateway:
    def __init__(self):
        """
        Initializes the pipeline components.
        Failed initialization of the Scrubber is a 'Critical Failure'.
        """
        try:
            logging.info("Initializing Security Layer (Local Scrubber)...")
            self.security_layer = LocalPIIScrubber()
            
            logging.info("Initializing Intelligence Layer (Cloud Evaluator)...")
            self.intelligence_layer = ClinicalEvaluator()
            
            logging.info("Gateway ready. Security protocols active.")
            
        except Exception as e:
            logging.critical(f"System Startup Failed: {e}")
            raise RuntimeError("Could not initialize Health AI Gateway.")

    def process_transaction(self, raw_query: str, raw_context: str, raw_response: str) -> dict:
        """
        Executes the Secure Evaluation Pipeline.
        Process Flow: Receive Data -> Scrub PII -> Send to Cloud -> Return Score
        """
        
        # --- Step 1: Security Audit (Local Execution) ---
        logging.info("Step 1: Scrubbing sensitive data locally...")
        
        safe_query, query_pii = self.security_layer.scrub_text(raw_query)
        safe_context, context_pii = self.security_layer.scrub_text(raw_context)
        safe_response, response_pii = self.security_layer.scrub_text(raw_response)
        
        total_pii_detected = len(query_pii) + len(context_pii) + len(response_pii)
        
        if total_pii_detected > 0:
            logging.warning(f"PII Detected and Redacted. Count: {total_pii_detected}")
        else:
            logging.info("No PII detected in transaction.")

        # --- Step 2: Clinical Evaluation (Cloud Execution) ---
        logging.info("Step 2: Sending sanitized data to Gemini for evaluation...")
        
        try:
            evaluation_result = self.intelligence_layer.evaluate_transaction(
                query=safe_query,
                context=safe_context,
                response=safe_response
            )
            logging.info("Evaluation complete. Score received.")
            
        except Exception as e:
            logging.error(f"Cloud Evaluation failed: {e}")
            return {"error": "Evaluation Service Unavailable", "status": 503}

        # --- Step 3: Result Synthesis ---
        final_report = {
            "status": "success",
            "security_audit": {
                "pii_detected": bool(total_pii_detected > 0),
                "redacted_entity_types": list(set(query_pii + context_pii + response_pii))
            },
            "clinical_quality": evaluation_result
        }
        
        return final_report