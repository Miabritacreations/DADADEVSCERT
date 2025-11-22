from urllib.parse import quote_plus

from backend.app.config import settings


class LinkedInService:
    SHARE_BASE = "https://www.linkedin.com/sharing/share-offsite/?url="

    def __init__(self, base_url: str = settings.BASE_URL):
        self.base_url = base_url

    def share_url(self, cert_id: str) -> str:
        verify_url = f"{self.base_url}/verify/{cert_id}"
        return f"{self.SHARE_BASE}{quote_plus(verify_url)}"

