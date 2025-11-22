# Dada Devs Blockchain Certificate Platform

Modernized issuance + verification stack for [Dada Devs](https://dadadevs.com/) demo deployments. The platform now delivers:

- Flask-based modular backend (web, admin, REST API blueprints)
- Ed25519 public/private key signatures (cryptography)
- Bitcoin anchoring via OpenTimestamps proofs
- Certificate revocation workflow + dashboard controls
- LinkedIn share links and optional IPFS public payload storage
- Responsive Tailwind UI for admin + verification pages
- Bulk CSV issuance, PDF + QR generation, SHA256 canonical payloads

---

## Directory structure

```
backend/
  app/
    __init__.py
    config.py
    utils.py
    routes/
      __init__.py
      admin.py
      api.py
      web.py
    services/
      certificate_service.py
      storage_service.py
      signature_service.py
      pdf_service.py
      ots_service.py
      ipfs_service.py
      linkedin_service.py
    templates/
      base.html
      landing.html
      verify.html
      admin/
        dashboard.html
        history.html
    static/
      css/app.css
      js/app.js
  data/
    certs.json
    ots/
  keys/
docs/
  architecture.md
app.py
requirements.txt
```

---

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# or: source .venv/bin/activate
pip install -r requirements.txt
```

Environment variables (optional):

```
BASE_URL=https://certs.dadadevs.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=supersecret
ENABLE_OTS=true
IPFS_API_URL=https://api.pinata.cloud/pinning/pinJSONToIPFS
IPFS_API_KEY=...
IPFS_API_SECRET=...
```

Run locally:

```bash
python app.py
```

Visit:
- `http://localhost:5000/` – landing + public issuance demo
- `http://localhost:5000/admin` – admin dashboard (issue, bulk, revoke, history)
- `http://localhost:5000/api/v1/...` – REST API

---

## Key components

- **SignatureService** – Ed25519 key generation + signing (PEM stored in `backend/keys`)
- **CertificateService** – orchestrates issuance, PDF/QR creation, OTS anchoring, LinkedIn/IPFS metadata, revocation
- **OpenTimestampsService** – stamps canonical payload hashes and stores `.ots` proofs
- **IPFSService** – optional Pinata-style JSON pinning (falls back to local storage)
- **Admin UI** – Tailwind dashboard with CSV uploads, revocation controls, history table
- **Verification UI** – shows signature validity, revocation state, Bitcoin timestamp proof, share link

See `docs/architecture.md` for the block diagram.

---

## REST API examples

Issue certificate:

```
POST /api/v1/certificates
{
  "name": "Wandia Mugo",
  "cohort": "Lightning Builders 2025",
  "email": "wandia@dadadevs.com"
}
```

Response:

```
201 Created
{
  "certificate": {
    "id": "uuid",
    "name": "...",
    "signature": "...",
    "verify_url": "...",
    "ots_status": "stamped",
    ...
  }
}
```

Verify certificate:

```
GET /api/v1/certificates/<id>
```

Revoke certificate:

```
POST /api/v1/certificates/<id>/revoke
{
  "reason": "Academic integrity violation"
}
```

Bulk issuance:

```
POST /api/v1/certificates/bulk
Content-Type: multipart/form-data
file=<csv file with name,cohort,email columns>
```

---

## LinkedIn & IPFS

- LinkedIn share links are auto-generated per certificate (`certificate.linkedin_share_url`).
- To publish public verification payloads on IPFS, set `IPFS_API_URL` (+ keys). Without it, JSON is stored locally under `backend/data/public`.

---

## Notes for hackathon demo

- All persistence uses JSON files for simplicity. Swap `CertificateStore` with PostgreSQL/Dynamo for production.
- OpenTimestamps requires network connectivity; if unavailable, proofs are marked `disabled` but still logged.
- Ed25519 public key is auto-exposed in templates for independent verification flows.
