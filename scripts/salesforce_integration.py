import os
import sys
import json
import subprocess
from typing import List, Dict

# Add root directory to python path for src module resolution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simple_salesforce import Salesforce, SalesforceError
from dotenv import load_dotenv
from src.pipeline import SalesforceDataPipeline

# Load credentials from .env
load_dotenv()

def get_salesforce_connection(org_type: str = "PROD") -> Salesforce:
    """Helper to authenticate to Salesforce based on org_type or local sf CLI session"""
    prefix = f"{org_type}_"
    
    username = os.environ.get(f"{prefix}SF_USERNAME")
    password = os.environ.get(f"{prefix}SF_PASSWORD")
    token = os.environ.get(f"{prefix}SF_TOKEN")
    
    if username and password:
        try:
            sf = Salesforce(
                username=username,
                password=password,
                security_token=token,
                domain="test" if org_type == "SANDBOX" else "login"
            )
            print(f"[+] Successfully connected to {org_type} Org via .env")
            return sf
        except Exception as e:
            print(f"[-] Failed to connect to {org_type} Org via .env: {e}")
            
    # Fallback to local sf CLI if credentials aren't in .env
    print(f"[*] No credentials found for {org_type} in .env. Attempting to use local Salesforce CLI session...")
    try:
        # Ask sf for the current access token
        # Adding shell=True is highly recommended on Windows when executing .cmd global scripts like sf
        result = subprocess.run(['sf', 'org', 'display', '--json'], capture_output=True, text=True, check=True, shell=True)
        org_data = json.loads(result.stdout).get("result", {})
        
        access_token = org_data.get("accessToken")
        instance_url = org_data.get("instanceUrl")
        
        if access_token and instance_url:
            sf = Salesforce(session_id=access_token, instance_url=instance_url)
            print(f"[+] Successfully connected to CLI Auth Org: {instance_url}")
            return sf
            
    except Exception as e:
        print(f"[-] Failed to connect via local Salesforce CLI: {e}")
        print("\n[!] To fix this, securely login via your browser by running this in your terminal:\n")
        print("    sf org login web\n")
        print("Then run this Python script again!")
        
    return None

def extract_production_data(sf_prod: Salesforce) -> List[Dict]:
    """Query Production for actual records containing PII."""
    print("[*] Querying Contact records from Production...")
    
    # Example query: getting 2 Contacts with standard fields to avoid permission issues
    query = "SELECT Id, LastName, Title FROM Contact WHERE LastName != NULL LIMIT 2"
    
    try:
        result = sf_prod.query(query)
        records = result.get('records', [])
        
        # simple-salesforce adds an 'attributes' key to each record. We remove it for clean processing.
        for record in records:
            if 'attributes' in record:
                del record['attributes']
                
        print(f"[+] Extracted {len(records)} records from Production")
        return records
    except SalesforceError as e:
        print(f"[-] Error querying Production: {e}")
        return []

def push_to_sandbox(sf_sandbox: Salesforce, records: List[Dict]):
    """Update Sandbox records with the anonymized data."""
    if not records:
        print("[-] No records to push.")
        return
        
    print(f"[*] Pushing {len(records)} sanitized records to Sandbox...")
    
    # We use bulk API or iterative updates using simple-salesforce
    try:
        # Warning: For update to work, the Sandbox MUST have records with these matching Ids. 
        # Usually Sandbox data is copied from Prod, meaning Ids are identical.
        # Alternatively, you could do an upsert on an External ID if needed.
        
        # simple_salesforce bulk update takes a list of dicts. Each must contain the 'Id'.
        results = sf_sandbox.bulk.Contact.update(records)
        
        success_count = sum(1 for res in results if res.get('success'))
        print(f"[+] Successfully updated {success_count}/{len(records)} records in Sandbox!")
        
    except Exception as e:
        print(f"[-] Error updating Sandbox: {e}")

def run_integration():
    print("=====================================================")
    print("--- Starting Salesforce Data Anonymization Flow ---")
    print("=====================================================\n")
    
    # 1. Connect to both Orgs
    sf_prod = get_salesforce_connection("PROD")
    sf_sandbox = get_salesforce_connection("SANDBOX")
    
    if not sf_prod or not sf_sandbox:
        print("[-] Missing Salesforce connections. Please check your .env file.")
        return
        
    # 2. Extract Data from Production
    production_records = extract_production_data(sf_prod)
    if not production_records:
        return
        
    # 3. Initialize the PII Anonymization Pipeline
    print("\n[*] Initializing Local AI Anonymizer Engine...")
    pipeline = SalesforceDataPipeline()
    fields_to_scrub = ["LastName", "Title"]
    
    # 4. Process Data In-Memory
    print("[*] Processing records through the AI to sanitize PII...")
    safe_records = pipeline.process_records(production_records, fields_to_scrub)
    
    # 5. Push Sanitized Data to Sandbox
    print("\n[*] Uploading results...")
    push_to_sandbox(sf_sandbox, safe_records)
    
    print("\n--- Pipeline Complete ---")

if __name__ == "__main__":
    run_integration()
