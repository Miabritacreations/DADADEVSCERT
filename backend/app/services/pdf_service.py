# Dada Devs Certificate PDF generator
# Standalone module that produces a certificate matching the provided mockup style.
# No hard-coded personal names are included — signature labels are placeholders.
# Uses the uploaded mockup image (if present) at /mnt/data/6c499ec9-fab1-4f61-8cc5-ed990388bba9.png for reference/watermark.

from io import BytesIO
from typing import Dict, List, Optional
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
import os

MOCKUP_IMAGE_PATH = "/mnt/data/6c499ec9-fab1-4f61-8cc5-ed990388bba9.png"

class PDFService:
    def __init__(self, base_url: str = "https://example.com") -> None:
        self.base_url = base_url
        # Palette tuned to match the mockup image colors
        self.deep_red = HexColor("#9B1C28")
        self.maroon = HexColor("#7A0C15")
        self.bright_orange = HexColor("#FF6B00")
        self.gold_light = HexColor("#F5D48F")
        self.gold_dark = HexColor("#C48C22")
        self.charcoal = HexColor("#231F20")
        self.sand = HexColor("#FFF4EB")
        self.text_muted = HexColor("#6B6B6B")
        self.paper = HexColor("#FFFCF7")
        self.border_muted = HexColor("#E8E3DA")

    def generate_pdf(self, cert: Dict, left_signatory: Optional[str] = None, left_title: Optional[str] = None, right_signatory: Optional[str] = None, right_title: Optional[str] = None) -> BytesIO:
        """Generate a certificate PDF.

        cert should include keys: name, id, signature, cohort, issued_at
        signatory and title fields are optional and default to empty placeholders.
        """
        buffer = BytesIO()
        width, height = landscape(A4)
        c = canvas.Canvas(buffer, pagesize=(width, height))

        # Optional background watermark using the uploaded mockup image (if available).
        if os.path.exists(MOCKUP_IMAGE_PATH):
            try:
                img = ImageReader(MOCKUP_IMAGE_PATH)
                c.saveState()
                c.translate(0, 0)
                c.drawImage(img, 0, 0, width=width, height=height, mask='auto', preserveAspectRatio=True, anchor='c')
                c.restoreState()
            except Exception:
                pass

        # Clean paper background with subtle border
        c.setFillColor(self.paper)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        margin = 36
        c.setStrokeColor(self.border_muted)
        c.setLineWidth(1.2)
        c.roundRect(margin - 8, margin - 8, width - 2 * (margin - 8), height - 2 * (margin - 8), 22, stroke=1, fill=0)
        c.setStrokeColor(self.deep_red)
        c.setLineWidth(2.2)
        c.roundRect(margin, margin, width - 2 * margin, height - 2 * margin, 18, stroke=1, fill=0)

        # Top logo only
        self._draw_logo(c, (width / 2) - 120, height - margin - 10)

        # Main body content
        cursor_y = height - margin - 120
        c.setFillColor(self.deep_red)
        c.setFont("Helvetica-Bold", 34)
        c.drawCentredString(width / 2, cursor_y, "Certificate of Achievement")
        cursor_y -= 46

        c.setFillColor(self.charcoal)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, cursor_y, "This certificate is proudly presented to")
        cursor_y -= 32

        c.setFont("Helvetica-Bold", 30)
        recipient = cert.get("name", " ").strip().upper()
        if recipient:
            c.drawCentredString(width / 2, cursor_y, recipient)
        else:
            line_w = 420
            c.setStrokeColor(self.deep_red)
            c.setLineWidth(1.2)
            c.line(width / 2 - line_w / 2, cursor_y - 6, width / 2 + line_w / 2, cursor_y - 6)
        cursor_y -= 40

        body = cert.get("body", (
            "In recognition of outstanding performance within the Dada Devs community. "
            "You have demonstrated collaboration, creativity, and impact across the Lightning and Web3 ecosystem."
        ))
        c.setFont("Helvetica", 11)
        c.setFillColor(self.charcoal)
        for line in self._wrap_lines(body, 90):
            c.drawCentredString(width / 2, cursor_y, line)
            cursor_y -= 16
        cursor_y -= 10

        cohort = cert.get("cohort", "-")
        issued_at = cert.get("issued_at", "-") or "-"
        issued_short = issued_at[:10] if isinstance(issued_at, str) and len(issued_at) >= 10 else issued_at
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(self.deep_red)
        c.drawCentredString(width / 2, cursor_y, f"Cohort: {cohort}   •   Issued: {issued_short}")

        # Signature section
        sig_base_y = margin + 120
        sig_width = 220
        left_sig_x = margin + 40
        right_sig_x = left_sig_x + sig_width + 120
        c.setStrokeColor(self.deep_red)
        c.setLineWidth(1.2)
        c.line(left_sig_x, sig_base_y, left_sig_x + sig_width, sig_base_y)
        c.line(right_sig_x, sig_base_y, right_sig_x + sig_width, sig_base_y)

        self._draw_signatory_block(
            c,
            left_sig_x + sig_width / 2,
            sig_base_y - 16,
            left_signatory,
            left_title
        )
        self._draw_signatory_block(
            c,
            right_sig_x + sig_width / 2,
            sig_base_y - 16,
            right_signatory or "DADA DEVS COUNCIL",
            right_title or "Program Leadership"
        )

        # QR (bottom-right, minimal)
        verify_url = f"{self.base_url}/verify/{cert.get('id','') if cert.get('id') else ''}"
        qr = qrcode.QRCode(box_size=5, border=1)
        qr.add_data(verify_url)
        qr.make()
        qr_buffer = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)
        qr_size = 70
        qr_right = width - margin - 40
        qr_bottom = margin + 20
        c.setFillColor(self.border_muted)
        c.roundRect(qr_right - qr_size - 14, qr_bottom - 14, qr_size + 28, qr_size + 28, 10, fill=1, stroke=0)
        c.setStrokeColor(self.deep_red)
        c.setLineWidth(0.6)
        c.roundRect(qr_right - qr_size - 14, qr_bottom - 14, qr_size + 28, qr_size + 28, 10, stroke=1, fill=0)
        c.drawImage(qr_reader, qr_right - qr_size, qr_bottom, width=qr_size, height=qr_size)

        # Footer provenance line
        c.setFont("Helvetica", 9)
        c.setFillColor(self.text_muted)
        c.drawCentredString(width / 2, margin + 30, "Secured with Ed25519 signatures, OpenTimestamps anchoring, and Bitcoin provenance.")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def _draw_logo(self, c: canvas.Canvas, x: float, y: float):
        """Draw Dada Devs logo: </> code tag with text."""
        # Code tag symbol: </> with orange/yellow colors
        tag_size = 24
        tag_y = y - tag_size
        
        # Left angle bracket < (orange)
        c.setFillColor(self.bright_orange)
        c.setFont("Helvetica-Bold", tag_size)
        c.drawString(x, tag_y, "<")
        
        # Forward slash / (orange)
        c.drawString(x + tag_size * 0.4, tag_y, "/")
        
        # Right angle bracket > (gold)
        c.setFillColor(self.gold_dark)
        c.drawString(x + tag_size * 0.8, tag_y, ">")
        
        # Text: "DADA DEVS"
        c.setFillColor(self.charcoal)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + tag_size * 1.3, y - 8, "DADA DEVS")
        
        # Text: "₿UIDL 4 AFRICA" (with Bitcoin symbol)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + tag_size * 1.3, y - 24, "₿UIDL 4 AFRICA")

    def _draw_signatory_block(self, c: canvas.Canvas, center_x: float, start_y: float, names, title: Optional[str]):
        """Render one or multiple signatory names stacked neatly above the title."""
        lines = self._normalize_name_lines(names)
        c.setFillColor(self.charcoal)
        c.setFont("Helvetica-Bold", 10)
        current_y = start_y
        for line in lines:
            c.drawCentredString(center_x, current_y, line)
            current_y -= 14
        if title:
            c.setFont("Helvetica", 9)
            c.drawCentredString(center_x, current_y - 4, title)

    @staticmethod
    def _normalize_name_lines(raw) -> List[str]:
        """Allow comma, slash, pipe, or newline separated names to display on their own rows."""
        if not raw:
            return []
        if isinstance(raw, (list, tuple)):
            parts = [str(item).strip() for item in raw if str(item).strip()]
        else:
            text = str(raw)
            for sep in ["/", "|", ","]:
                text = text.replace(sep, "\n")
            parts = [seg.strip() for seg in text.splitlines() if seg.strip()]
        return [part.upper() for part in parts] or []

    @staticmethod
    def _wrap_lines(text: str, width: int) -> List[str]:
        words = text.split()
        lines: List[str] = []
        current: List[str] = []
        count = 0
        for word in words:
            spacer = 1 if current else 0
            if count + len(word) + spacer > width:
                lines.append(" ".join(current))
                current = [word]
                count = len(word)
            else:
                current.append(word)
                count += len(word) + spacer
        if current:
            lines.append(" ".join(current))
        return lines

# Example usage (uncomment to test locally)
# if __name__ == "__main__":
#     svc = PDFService(base_url="https://dada.example")
#     cert = {
#         "name": "",
#         "id": "cert_0123456789abcdef",
#         "signature": "abcdef1234567890fedcba",
#         "cohort": "2025",
#         "issued_at": "2025-11-23T00:00:00Z",
#     }
#     pdf = svc.generate_pdf(cert)
#     with open("dada_certificate.pdf", "wb") as f:
#         f.write(pdf.read())

