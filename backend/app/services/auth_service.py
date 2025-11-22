"""Authentication and identity verification services."""
from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib
import secrets
import json
from pathlib import Path
from typing import Optional, Dict
from backend.app.config import settings


class AuthService:
    """Handles admin authentication and student identity verification."""
    
    def __init__(self):
        self.session_file = settings.DATA_DIR / "sessions.json"
        self.student_verifications_file = settings.DATA_DIR / "student_verifications.json"
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure session and verification files exist."""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.session_file.exists():
            self.session_file.write_text("{}", encoding="utf-8")
        if not self.student_verifications_file.exists():
            self.student_verifications_file.write_text("{}", encoding="utf-8")
    
    def verify_admin(self, username: str, password: str) -> bool:
        """Verify admin credentials."""
        return (
            username == settings.ADMIN_USERNAME and
            password == settings.ADMIN_PASSWORD
        )
    
    def login_admin(self, username: str, password: str) -> bool:
        """Login admin and create session."""
        if self.verify_admin(username, password):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            return True
        return False
    
    def logout_admin(self):
        """Logout admin."""
        session.pop("admin_logged_in", None)
        session.pop("admin_username", None)
    
    def is_admin_logged_in(self) -> bool:
        """Check if admin is logged in."""
        return session.get("admin_logged_in", False)
    
    def generate_student_verification_token(self, email: str, cert_id: str) -> str:
        """Generate a verification token for student identity."""
        token = secrets.token_urlsafe(32)
        verifications = self._load_verifications()
        verifications[token] = {
            "email": email,
            "cert_id": cert_id,
            "verified": False,
            "created_at": None
        }
        self._save_verifications(verifications)
        return token
    
    def verify_student_token(self, token: str) -> Optional[Dict]:
        """Verify a student token and mark as verified."""
        verifications = self._load_verifications()
        if token in verifications:
            verifications[token]["verified"] = True
            self._save_verifications(verifications)
            return verifications[token]
        return None
    
    def check_student_verified(self, email: str, cert_id: str) -> bool:
        """Check if student email is verified for a certificate."""
        verifications = self._load_verifications()
        for v in verifications.values():
            if v.get("email") == email and v.get("cert_id") == cert_id and v.get("verified"):
                return True
        return False
    
    def _load_verifications(self) -> Dict:
        """Load verification data."""
        try:
            return json.loads(self.student_verifications_file.read_text(encoding="utf-8"))
        except:
            return {}
    
    def _save_verifications(self, data: Dict):
        """Save verification data."""
        self.student_verifications_file.write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )


def require_admin(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_service = AuthService()
        if not auth_service.is_admin_logged_in():
            if request.is_json:
                return jsonify({"error": "Authentication required"}), 401
            flash("Please log in to access admin area", "error")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated_function

