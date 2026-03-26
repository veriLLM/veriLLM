# DPIA Documentation for veriLLM

## Document Objective
This Data Protection Impact Assessment (DPIA) document captures privacy risks and controls for the veriLLM pipeline that sanitizes production text records before sandbox use.

## Processing Overview
- Source: Production Salesforce records containing unstructured text.
- Activity: Automated detection and replacement of PII with synthetic equivalents.
- Destination: Sandbox environment for development and testing.
- Method: Local model inference and pipeline orchestration.

## Necessity and Proportionality
- The processing supports legitimate engineering testing workflows.
- The anonymization step reduces direct exposure of personal data in lower-security environments.
- Data collection is limited to required fields and record sets.
- Processing avoids persistent storage of raw personal data where possible.

## Data Categories
- Contact identifiers: names, emails, phone numbers.
- Government identifiers: national IDs/SSNs in free text.
- Location details: addresses present in case comments or descriptions.

## Stakeholders
- Controller representative (business owner).
- Security team.
- Engineering owner of extraction and sandbox injection.
- Privacy/legal reviewer.

## Risk Assessment
- Risk: Raw PII appears in debug logs.
  - Impact: Unauthorized disclosure.
  - Mitigation: Secure log filtering and strict logging standards.
- Risk: Secrets exposed in source code or config files.
  - Impact: Unauthorized system access.
  - Mitigation: Environment variable based credential loading and secret governance.
- Risk: Incomplete anonymization leaves residual PII.
  - Impact: Privacy breach in sandbox.
  - Mitigation: Model prompt constraints, fallback masking, and periodic quality checks.
- Risk: Data exported to local files during troubleshooting.
  - Impact: Uncontrolled data retention.
  - Mitigation: Prohibit local dumps of unsanitized records and enforce operational runbooks.

## Control Checklist
- [ ] Approved lawful basis documented by controller.
- [ ] Field-level minimization list reviewed and approved.
- [ ] Logging policy reviewed for PII-safe output.
- [ ] Incident response owner and escalation path assigned.
- [ ] Retention and deletion strategy documented.
- [ ] Access to production credentials restricted and audited.

## Residual Risk and Sign-Off
- Residual risk remains low to medium depending on model quality and operational discipline.
- Final acceptance requires review and sign-off by privacy/legal and security stakeholders.

## Review Cadence
- Review after major architecture changes.
- Reassess before onboarding new data objects or jurisdictions.
- Minimum periodic review interval: every 6 months.
