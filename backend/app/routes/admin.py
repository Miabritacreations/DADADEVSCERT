from __future__ import annotations

import io

from flask import flash, redirect, render_template, request, send_file, url_for

from backend.app.routes import admin_bp
from backend.app.services.auth_service import AuthService, require_admin
from backend.app.services.certificate_service import CertificateService


def init_admin_routes(service: CertificateService) -> None:
    auth_service = AuthService()
    
    @admin_bp.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if auth_service.login_admin(username, password):
                flash("Logged in successfully", "success")
                return redirect(url_for("admin.dashboard"))
            else:
                flash("Invalid credentials", "error")
        return render_template("admin/login.html")
    
    @admin_bp.route("/logout", methods=["POST"])
    def logout():
        auth_service.logout_admin()
        flash("Logged out successfully", "success")
        return redirect(url_for("admin.login"))
    
    @admin_bp.route("/", methods=["GET"])
    @require_admin
    def dashboard():
        certs = service.list_history()
        stats = {
            "total": len(certs),
            "revoked": len([c for c in certs if c.get("revoked")]),
            "active": len([c for c in certs if not c.get("revoked")]),
        }
        return render_template("admin/dashboard.html", certificates=certs[:10], stats=stats)

    @admin_bp.route("/history", methods=["GET"])
    @require_admin
    def history():
        certs = service.list_history()
        return render_template("admin/history.html", certificates=certs)

    @admin_bp.route("/issue", methods=["POST"])
    @require_admin
    def issue():
        name = request.form.get("name")
        cohort = request.form.get("cohort", "unspecified")
        email = request.form.get("email")
        if not name:
            flash("Name is required", "error")
            return redirect(url_for("admin.dashboard"))
        cert, pdf_bytes = service.issue(name=name, cohort=cohort, email=email)
        flash(f"Certificate issued for {name}", "success")
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f"certificate-{cert['id']}.pdf",
            mimetype="application/pdf",
        )

    @admin_bp.route("/bulk", methods=["POST"])
    @require_admin
    def bulk_issue():
        file = request.files.get("csv_file")
        if not file:
            flash("CSV file is required", "error")
            return redirect(url_for("admin.dashboard"))
        issued = service.bulk_issue(file.read())
        flash(f"Issued {len(issued)} certificates from CSV", "success")
        return redirect(url_for("admin.history"))

    @admin_bp.route("/revoke/<cert_id>", methods=["POST"])
    @require_admin
    def revoke(cert_id: str):
        reason = request.form.get("reason", "No reason provided")
        cert = service.revoke(cert_id, reason)
        if not cert:
            flash("Certificate not found", "error")
        else:
            flash(f"Revoked certificate {cert_id}", "warning")
        return redirect(url_for("admin.history"))

