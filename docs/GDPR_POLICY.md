# GDPR Policy for veriLLM

## Purpose
This policy defines how the veriLLM project handles personal data in alignment with the General Data Protection Regulation (GDPR) when sanitizing data before non-production use.

## Scope
This policy applies to:
- Data extracted from production Salesforce environments.
- Intermediate processing performed by the AI anonymization pipeline.
- Sanitized outputs sent to lower-security development or testing environments.

## Roles and Responsibilities
- Data Controller: Organization owning the production Salesforce data.
- Data Processor: veriLLM pipeline components executing anonymization on controller instructions.
- Engineering Team: Ensures technical controls are implemented and followed.

## GDPR Principles Applied
- Lawfulness, fairness, and transparency: Processing occurs only for approved development and testing purposes.
- Purpose limitation: Data is used only for anonymization and controlled sandbox population.
- Data minimization: Only required objects and fields are queried and processed.
- Accuracy: Source records remain unchanged; sanitized records preserve business context.
- Storage limitation: Raw personal data must not be stored in local files or long-term logs.
- Integrity and confidentiality: Isolated runtime, least privilege, and secure logging controls are required.
- Accountability: Processing runs should be auditable with non-PII operational logs.

## Data Handling Requirements
- Never hardcode credentials, tokens, or secrets in source code.
- Load credentials from environment variables or approved secret managers.
- Do not print or log full records that may contain personal data.
- Do not export unsanitized records to local CSV, JSON, or debug dumps.
- Process only approved unstructured fields for anonymization.

## Security Controls
- In-memory handling for sensitive records whenever possible.
- Network segmentation for model inference components.
- Non-root runtime for containerized services.
- Logging filters to reduce accidental PII exposure.
- Safe fallback behavior when anonymization fails.

## Data Subject Rights Support
Where applicable, controller teams must be able to:
- Locate processing context by record identifiers.
- Correct or remove upstream records before processing.
- Pause or stop processing jobs for objection or legal requests.

## Incident Response
- Any suspected PII leakage must be treated as a security incident.
- Stop active processing and preserve non-sensitive forensic logs.
- Notify security and compliance stakeholders promptly.
- Assess regulatory notification obligations under GDPR timelines.

## Review and Maintenance
- Review this policy at least every 6 months or after major architecture changes.
- Update controls when legal, regulatory, or platform requirements change.
