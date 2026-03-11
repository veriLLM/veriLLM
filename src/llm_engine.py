import logging
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger("SecureLogger")

class PIIAnonymizer:
    def __init__(self, model_name="llama3", base_url="http://ollama:11434"):
        # We point to our internal isolated Ollama container
        self.llm = Ollama(model=model_name, base_url=base_url, temperature=0.1)
        
        # We need a strict prompt to ensure AI focuses ONLY on redaction and avoids talking to the user.
        self.prompt = PromptTemplate(
            input_variables=["text"],
            template="""You are a strict Data Privacy Compliance Officer. Your ONLY job is to find Personally Identifiable Information (PII) in the following text and replace it with highly realistic synthetic data.

Rules:
1. Identify all Names, Email Addresses, Phone Numbers, SSNs, and Physical Addresses.
2. Replace each identified entity with a fake but realistic equivalent (e.g., replace a real name with "John Doe", a real email with "jdoe@example.com", and a real 9-digit SSN with "000-00-0000").
3. Preserve the exact meaning and structure of the original text.
4. Output NOTHING but the final anonymized text. Do not add any conversational filler, explanations, or notes.

Original Text:
{text}

Anonymized Text:"""
        )

    def anonymize_text(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return text
            
        try:
            chain = self.prompt | self.llm
            result = chain.invoke({"text": text})
            return result.strip()
        except Exception as e:
            # [CYBERSEC] Error Handling without PII Leakage
            # We explicitly do not log the text that caused the crash.
            logger.error("Error during LLM anonymization. Fallback triggered to prevent leakage.")
            return "[REDACTED_DUE_TO_PROCESSING_ERROR]"
