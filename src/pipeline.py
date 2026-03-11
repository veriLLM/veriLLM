import os
from typing import List, Dict
from src.llm_engine import PIIAnonymizer
from src.utils.secure_logger import get_secure_logger

logger = get_secure_logger()

class SalesforceDataPipeline:
    def __init__(self):
        # Allow checking if we are testing locally without docker (where ollama might be on localhost)
        ollama_base = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.anonymizer = PIIAnonymizer(base_url=ollama_base)
        
    def process_records(self, records: List[Dict], fields_to_anonymize: List[str]) -> List[Dict]:
        """
        Orchestrates the data flow. Takes real Salesforce records, runs the specified
        unstructured text fields through the LLM, and returns sanitized records.
        """
        logger.info(f"Starting pipeline processing for {len(records)} records.")
        sanitized_records = []
        
        for idx, record in enumerate(records):
            # Create a shallow copy to avoid mutating the original production data in memory
            safe_record = record.copy()
            
            for field in fields_to_anonymize:
                if field in safe_record and isinstance(safe_record[field], str):
                    original_text = safe_record[field]
                    try:
                        # Pass through our Local LLM Engine
                        sanitized_text = self.anonymizer.anonymize_text(original_text)
                        safe_record[field] = sanitized_text
                    except Exception as e:
                        logger.error(f"Failed to anonymize field {field} in record index {idx}")
                        safe_record[field] = "[REDACTED_FALLBACK]"
            
            sanitized_records.append(safe_record)
            logger.info(f"Successfully processed record index {idx}")
            
        logger.info("Pipeline processing complete.")
        return sanitized_records
