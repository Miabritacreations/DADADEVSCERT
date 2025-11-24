# Dada Devs Digital Certificate Signature System – MVP Submission

## Overview

This repository hosts the working MVP requested in the DADA DEVS MVP Challenge. It delivers a full end-to-end digital certificate issuance and verification flow built with Flask, ReportLab, qrcode, Ed25519 signatures, and optional OpenTimestamps anchoring. Certificates are rendered as PDFs with embedded signatures, metadata, and a QR code that links to the verification endpoint.

## How It Works

1. **Unique Certificate ID**  
   Certificates are assigned UUID-style identifiers (`cert["id"]`). They are stored alongside all issued metadata in `backend/data/certs.json`.

2. **Tamper-Proof Signature**  
   - The backend uses Ed25519 keys (generated once under `backend/keys/`) to sign the canonical JSON payload of each certificate.  
   - The signature is embedded directly in every certificate PDF and appears on the verification page.  
   - Optionally the hash can be anchored with OpenTimestamps to log a Bitcoin proof.

3. **QR Code Attachment**  
   - `backend/app/services/pdf_service.py` embeds a QR code near the signature section.  
   - Scanning leads to `GET /verify/<certificate_id>` which re-validates the signature and displays the trust status (valid/revoked/tampered).

4. **Verification Workflow**  
   - Verification pages are powered by the Flask `web` blueprint.  
   - A certificate is authentic only if the stored data, digital signature, and revocation flag pass validation.  
   - Tampered payloads or revoked cert IDs are clearly flagged to the viewer.

5. **Admin Issuance Flow**  
   - Run `python app.py`, then visit `http://localhost:5000/admin`.  
   - Admin dashboard provides:
     - Single issuance form (name, cohort, email, optional message).  
     - Bulk issuance via CSV upload.  
     - Revocation controls and issuance history.  
   - Each issuance triggers PDF generation, QR embedding, signature creation, and storage in JSON.

## Steps to Issue a Certificate

1. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```
2. Run the service:
   ```
   python app.py
   ```
3. Open `http://localhost:5000/admin`.  
4. Fill in the single-issue form: name, cohort, email, optional notes.  
5. Click “Submit for approval”. The system queues the request for admin review (stored in `backend/data/cert_requests.json`).  
6. Approve from the “Pending approvals” table to generate the signed PDF, metadata, and Bitcoin proof. Approved certificates are stored in `backend/data/certs.json`.

## Steps to Verify a Certificate

1. Scan the QR code on the certificate or browse to `http://localhost:5000/verify/<cert_id>`.  
2. The verification page fetches the stored cert payload, re-checks the Ed25519 signature, and reports:
   - Certificate details (name, cohort, issued date).  
   - Signature preview, hashes, and Bitcoin anchoring state.  
   - Revocation status with warnings if tampering is detected.

3. If the certificate has been revoked or the payload fails signature validation, the UI highlights the issue so recipients are warned immediately.

## Security Considerations

- **Public/Private Key Signing**: Certificates cannot be forged without access to the private Ed25519 key. All verification uses the public key bundled in the frontend templates.  
- **Immutable IDs & JSON Storage**: The canonical payload is stored in `certs.json`, and any mismatch between stored data and a PDF will cause signature verification to fail.  
- **Optional Bitcoin Anchoring**: When OpenTimestamps is enabled, the certificate hash is embedded into Bitcoin’s blockchain, giving long-term immutability proof.  
- **Revocation Support**: Admins can mark a cert as revoked; verification pages and QR results will switch to “revoked” immediately.  
- **QR Verification**: Each PDF includes a QR code that points to the live verification endpoint instead of static text, making cloned PDFs detectable.

## Sample Certificate

- Use the admin issuance flow to generate an example PDF. The certificate features:  
  - Single top logo  
  - Clean layout with centered copy  
  - Signature lines for two signatories  
  - Compact QR code with signature metadata beneath the signature area  
  - A footer describing the cryptographic guarantees

## README Checklist (already in repo)

- `README.md` contains project description, setup instructions, directory structure, and more detail on the services (CertificateService, SignatureService, PDFService, etc.).  
- For submissions, reference that README plus this `docs/submission.md` to demonstrate compliance with the challenge brief.

## Deliverables Summary

| Requirement                         | Implementation Detail |
|------------------------------------|------------------------|
| Unique Certificate ID              | UUID stored in JSON and rendered on PDFs |
| Tamper-proof digital signature     | Ed25519 signatures + optional OpenTimestamps |
| Signature embedded in certificate  | Signature preview & metadata block + QR code |
| QR code verification               | QR leads to `/verify/<id>` with real-time validation |
| Simple issuance flow               | Form submits to approval queue, dashboard approvals finalize issuance |

**Bonus features included:** revocation workflow, issuance history, IPFS publishing hooks, and a refreshed certificate design with logos, signature section, and verification QR as requested.

