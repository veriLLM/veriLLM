import logging

class SecureLogFilter(logging.Filter):
    """
    [CYBERSEC] Data Context Filtering
    This filter ensures that specific types of data (like full dictionaries which might contain PII) 
    are never accidentally logged to the console or log files.
    """
    def filter(self, record):
        if isinstance(record.msg, dict):
            # If a developer accidentally writes logger.info(user_record)
            # This intercepts it and stops the PII from hitting the disk or standard output.
            record.msg = "Attempted to log payload. Masked by SecureLogFilter to prevent PII leakage."
        return True

def get_secure_logger(name="SecureLogger"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add the secure filter
        ch.addFilter(SecureLogFilter())
        
        logger.addHandler(ch)
    return logger
