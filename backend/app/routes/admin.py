from __future__ import annotations

import io

from flask import flash, redirect, render_template, request, send_file, url_for, session

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
        pending_requests = service.list_requests(status="pending")
        stats = {
            "total": len(certs),
            "revoked": len([c for c in certs if c.get("revoked")]),
            "active": len([c for c in certs if not c.get("revoked")]),
            "pending": len(pending_requests),
        }
        return render_template(
            "admin/dashboard.html",
            certificates=certs[:10],
            pending_requests=pending_requests[:10],
            stats=stats,
        )

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
        service.request_issue(
            name=name,
            cohort=cohort,
            email=email,
            requested_by=session.get("admin_username"),
            source="admin_form",
        )
        flash(f"Certificate request created for {name}. Awaiting approval.", "info")
        return redirect(url_for("admin.dashboard"))

    @admin_bp.route("/bulk", methods=["POST"])
    @require_admin
    def bulk_issue():
        file = request.files.get("csv_file")
        if not file:
            flash("CSV file is required", "error")
            return redirect(url_for("admin.dashboard"))
        requests_created = service.bulk_request_issue(file.read(), requested_by=session.get("admin_username"))
        flash(f"Queued {len(requests_created)} certificate requests for approval.", "info")
        return redirect(url_for("admin.dashboard"))

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

    @admin_bp.route("/requests/<request_id>/approve", methods=["POST"])
    @require_admin
    def approve_request(request_id: str):
        result = service.approve_request(request_id, approver=session.get("admin_username"))
        if not result:
            flash("Request not found or already processed.", "error")
            return redirect(url_for("admin.dashboard"))
        cert, pdf_bytes = result
        flash(f"Approved certificate for {cert['name']}", "success")
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f"certificate-{cert['id']}.pdf",
            mimetype="application/pdf",
        )

    @admin_bp.route("/requests/<request_id>/reject", methods=["POST"])
    @require_admin
    def reject_request(request_id: str):
        reason = request.form.get("reason", "Rejected by admin")
        updated = service.reject_request(request_id, reviewer=session.get("admin_username"), reason=reason)
        if not updated:
            flash("Request not found or already processed.", "error")
        else:
            flash("Certificate request rejected.", "warning")
        return redirect(url_for("admin.dashboard"))

