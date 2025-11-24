"""
Small CLI to issue a certificate (sends request to running Flask app).

Usage examples:
    python issue_cert.py --name "Bridgit G" --cohort "DadaDevs Feb 2025"
    python issue_cert.py --server https://certs.dadadevs.com --name "Jane Doe" --out jane.pdf
"""

import requests
import argparse
import re
import sys

parser = argparse.ArgumentParser(description="Issue certificate via running DadaDevs Certificate server.")
parser.add_argument('--server', default='http://localhost:5000', help='Server base URL')
parser.add_argument('--name', required=True, help='Full name of learner')
parser.add_argument('--cohort', default='unspecified', help='Cohort name')
parser.add_argument('--out', default=None, help='Output PDF file name')
args = parser.parse_args()

try:
    print(f"→ Sending request to {args.server}/issue ...")
    resp = requests.post(
        f"{args.server}/issue",
        json={'name': args.name, 'cohort': args.cohort},
        timeout=15
    )
except Exception as e:
    print("❌ Network error:", e)
    sys.exit(1)

content_type = resp.headers.get('content-type', '')

if resp.status_code == 200 and 'application/pdf' in content_type:
    # sanitize filename
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', args.name)
    out = args.out or f"certificate-{safe_name}.pdf"
    with open(out, 'wb') as f:
        f.write(resp.content)
    print(f"✅ Certificate PDF saved to: {out}")

elif resp.status_code in (200, 202):
    # JSON fallback
    try:
        data = resp.json()
    except ValueError:
        print("⚠ Unexpected response (not JSON, not PDF):")
        print(resp.text)
        sys.exit(1)

    status = data.get("status")
    if status == "pending":
        req = data.get("request", {})
        print("⏳ Certificate request queued for admin approval.")
        if req:
            print(f"   request_id: {req.get('request_id')}")
            print(f"   learner: {req.get('name')}  cohort: {req.get('cohort')}")
            print("   Wait for an admin to approve and release the PDF.")
    else:
        print("📝 Server returned JSON response:")
        print(data)
        if "verify_url" in data:
            print("🔗 Verify at:", data["verify_url"])

else:
    print(f"❌ Error {resp.status_code} from server:")
    print(resp.text)
