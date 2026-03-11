# veriLLM: Execution & Integration Guide

Welcome to the **veriLLM DevSecOps Data Sanitization Pipeline**. This document explains how to execute the application locally for testing, how to run the secure containerized version, and provides a step-by-step guide for the Salesforce Developer to integrate their code with this cybersecurity engine.

---

## 🚀 Part 1: How to Execute and Test Locally

Before running the full Docker pipeline, you can test the AI Engine locally using our mock generated data.

### Prerequisites (for local testing)
1. **Python 3.10+** installed on your machine.
2. **Ollama**: You must have Ollama installed locally to run the Llama 3 model.
   - Download from [ollama.com](https://ollama.com/)
   - Open a terminal and run: `ollama run llama3` (This will download the model and start the local server on `http://localhost:11434`).

### Execution Steps
1. Open a terminal in the root of the `PII-REDACTOR` project.
2. Create a virtual environment and install the requirements (which we already created in `requirements.txt`):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the End-to-End Mock Engine test:
   ```bash
   python scripts/mock_generator.py
   ```
4. **Expected Output:** You should see the terminal print the original "Dangerous" JSON payload, wait a few moments as the LLM processes it, and then print the "Safe" JSON payload where names, SSNs, and emails have been replaced with fake, functional data.

---

## 🛡️ Part 2: Running the Secure Docker Environment

When deploying or running the true pipeline, we use Docker to ensure the **In-Memory Processing (tmpfs)** and **Microsegmentation** cybersecurity concepts are enforced.

### Execution Steps
1. Ensure Docker Desktop is running.
2. In the root directory, run:
   ```bash
   docker-compose up --build
   ```
3. This creates a secure, isolated network where our Python worker and the Ollama container communicate without ever writing sensitive target data to your physical hard drive.

---

## 🤝 Part 3: Guide for the Salesforce Developer (Your Friend)

Hello Salesforce Dev! Your job is to build the "Pipes" (Extraction and Injection) that connect to this "Brain" (The LLM Anonymizer). Here is exactly what you need to do step-by-step:

### Overview of Your Task
You are writing a Python script (e.g., `salesforce_integration.py`) that uses a library like `simple-salesforce` to pull Production records, pass them into our existing `SalesforceDataPipeline`, and push the sanitized results into the Sandbox.

### Step-by-Step Instructions

#### 1. Setup Authentication (Connected Apps)
- In the **Production Org**, create a Salesforce Connected App to get a `client_id`, `client_secret`, and set up OAuth 2.0 (or just an API token for testing).
- Repeat this process in the **Sandbox Org**.
- Store these credentials securely in the `.env` file. **Do not hardcode them in your script.**

#### 2. Write the Extraction Function `get_prod_data()`
- Query Production for the objects you want to sanitize (e.g., `Case`, `Contact`, `Lead`).
- Focus specifically on fields that contain unstructured text (like `Description`, `Case_Comment__c`, or `Chat_Transcript__c`).
- **Data Format Requirements:** Your function must return a **List of Dictionaries**, exactly like this:
  ```python
  [
      {
          "Id": "5003000000ABCDE", 
          "Description": "John Doe called, his SSN is 123-45-6789",
          "Status": "Closed"
      }
  ]
  ```

#### 3. Integrate with the Pipeline (The Handoff)
- Import our pipeline class into your script.
- Pass your extracted list of dictionaries to `pipeline.process_records()`.
- Tell the pipeline *exactly* which fields contain the unstructured text that needs to be anonymized.

**Example Integration Code:**
```python
from src.pipeline import SalesforceDataPipeline

def run_salesforce_job():
    # 1. Extract from Production (You build this)
    production_records = get_prod_data("SELECT Id, Description FROM Case LIMIT 10")
    
    # 2. Initialize the Cybersecurity AI Pipeline
    anonymizer_pipeline = SalesforceDataPipeline()
    
    # Define which fields the LLM should scrub for PII
    fields_to_scrub = ["Description"]
    
    # 3. Process the records securely
    # This will return the exact same dictionary structure, but the 'Description' 
    # field will be replaced with synthetic data.
    safe_sandbox_records = anonymizer_pipeline.process_records(production_records, fields_to_scrub)
    
    # 4. Inject to Sandbox (You build this)
    push_to_sandbox(safe_sandbox_records)
```

#### 4. Write the Injection Function `push_to_sandbox()`
- Take the `safe_sandbox_records` list returned by the pipeline.
- Iterate over the list and perform an `UPSERT` or `UPDATE` operation against the Sandbox Org using the `Id` field.
- **Cybersecurity Warning:** Never write the `production_records` or the `safe_sandbox_records` to a local `.csv` or `.json` file during this transition. Everything must remain in the Python memory space!
