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

# UPDATED: Use getLogger instead of basicConfig to avoid conflicts with app.py
logger = logging.getLogger(__name__)

class HealthAIGateway:
    def __init__(self):
        """
        Initializes the pipeline components.
        Failed initialization of the Scrubber is a 'Critical Failure'.
        """
        try:
            # UPDATED: Using module-level logger
            logger.info("Initializing Security Layer (Local Scrubber)...")
            self.security_layer = LocalPIIScrubber()
            
            logger.info("Initializing Intelligence Layer (Cloud Evaluator)...")
            self.intelligence_layer = ClinicalEvaluator()
            
            logger.info("Gateway ready. Security protocols active.")
            
        except Exception as e:
            logger.critical(f"System Startup Failed: {e}")
            raise RuntimeError("Could not initialize Health AI Gateway.")

    def process_transaction(self, raw_query: str, raw_context: str, raw_response: str) -> dict:
        """
        Executes the Secure Evaluation Pipeline.
        Process Flow: Receive Data -> Scrub PII -> Send to Cloud -> Return Score
        """
        
        # --- Step 1: Security Audit (Local Execution) ---
        logger.info("Step 1: Scrubbing sensitive data locally...")
        
        safe_query, query_pii = self.security_layer.scrub_text(raw_query)
        safe_context, context_pii = self.security_layer.scrub_text(raw_context)
        safe_response, response_pii = self.security_layer.scrub_text(raw_response)
        
        total_pii_detected = len(query_pii) + len(context_pii) + len(response_pii)
        
        if total_pii_detected > 0:
            logger.warning(f"PII Detected and Redacted. Count: {total_pii_detected}")
        else:
            logger.info("No PII detected in transaction.")

        # --- Step 2: Clinical Evaluation (Cloud Execution) ---
        logger.info("Step 2: Sending sanitized data to Gemini for evaluation...")
        
        try:
            evaluation_result = self.intelligence_layer.evaluate_transaction(
                query=safe_query,
                context=safe_context,
                response=safe_response
            )
            logger.info("Evaluation complete. Score received.")
            
        except Exception as e:
            logger.error(f"Cloud Evaluation failed: {e}")
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