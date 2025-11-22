from flask import Flask

from backend.app.config import settings
from backend.app.routes import admin_bp, api_bp, web_bp
from backend.app.routes.admin import init_admin_routes
from backend.app.routes.api import init_api_routes
from backend.app.routes.web import init_web_routes
from backend.app.services.certificate_service import CertificateService
from backend.app.services.ipfs_service import IPFSService
from backend.app.services.linkedin_service import LinkedInService
from backend.app.services.ots_service import OpenTimestampsService
from backend.app.services.pdf_service import PDFService
from backend.app.services.signature_service import SignatureService
from backend.app.services.storage_service import CertificateStore


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dadadevs-demo-secret"

    store = CertificateStore()
    signer = SignatureService()
    pdf_service = PDFService(base_url=settings.BASE_URL)
    ots_service = OpenTimestampsService()
    ipfs_service = IPFSService()
    linkedin_service = LinkedInService()

    cert_service = CertificateService(
        store=store,
        signer=signer,
        pdf_service=pdf_service,
        ots_service=ots_service,
        ipfs_service=ipfs_service,
        linkedin_service=linkedin_service,
    )

    init_admin_routes(cert_service)
    init_api_routes(cert_service)
    init_web_routes(cert_service)

    app.register_blueprint(web_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_public_key():
        return {"public_key_pem": signer.export_public_key_pem()}

    return app

