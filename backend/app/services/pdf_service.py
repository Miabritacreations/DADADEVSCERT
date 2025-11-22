# Dada Devs Certificate PDF generator
# Standalone module that produces a certificate matching the provided mockup style.
# No hard-coded personal names are included — signature labels are placeholders.
# Uses the uploaded mockup image (if present) at /mnt/data/6c499ec9-fab1-4f61-8cc5-ed990388bba9.png for reference/watermark.

from io import BytesIO
from typing import Dict, List, Optional
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfgen.pathobject import PDFPathObject
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
                # paint the mockup faintly as a watermark to help match layout when needed
                c.saveState()
                c.translate(0, 0)
                c.drawImage(img, 0, 0, width=width, height=height, mask='auto', preserveAspectRatio=True, anchor='c')
                c.restoreState()
            except Exception:
                # ignore watermark errors and continue drawing shapes programmatically
                pass

        # Background + bottom accent bars
        c.setFillColor(self.sand)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        c.setFillColor(self.bright_orange)
        c.rect(0, 0, width, 12, fill=1, stroke=0)
        c.setFillColor(self.maroon)
        c.rect(0, 12, width, 6, fill=1, stroke=0)

        # Left layered banners (programmatic shapes matching the mockup)
        left_panel_width = width * 0.33
        self._draw_polygon(c, [(0, height), (left_panel_width, height), (left_panel_width * 0.6, height - 240), (0, height - 80)], self.maroon)
        self._draw_polygon(c, [(0, height - 30), (left_panel_width * 0.98, height - 60), (left_panel_width * 0.55, height - 310), (0, height - 150)], self.bright_orange)

        # Gold ribbon and seal (angled)
        ribbon_y = height - 220
        ribbon_height = 34
        self._draw_polygon(c, [(left_panel_width * 0.32, ribbon_y + ribbon_height), (width * 0.78, ribbon_y + ribbon_height), (width * 0.74, ribbon_y), (left_panel_width * 0.32, ribbon_y)], self.gold_light)
        self._draw_polygon(c, [(left_panel_width * 0.32, ribbon_y - 6), (width * 0.76, ribbon_y - 6), (width * 0.73, ribbon_y - 12), (left_panel_width * 0.32, ribbon_y - 12)], self.gold_dark)

        # Circular seal with two-tone gold
        c.setFillColor(self.gold_dark)
        c.circle(left_panel_width * 0.42, ribbon_y + ribbon_height / 2, 50, fill=1, stroke=0)
        c.setFillColor(self.gold_light)
        c.circle(left_panel_width * 0.42, ribbon_y + ribbon_height / 2, 40, fill=1, stroke=0)
        
        # Dada Devs Logo (top right corner)
        self._draw_logo(c, width - 200, height - 80)

        # Content block centered to match mockup layout
        content_left = width * 0.38
        content_right = width * 0.88
        center_x = (content_left + content_right) / 2
        cursor_y = height - 120
        
        c.setFillColor(self.deep_red)
        c.setFont("Helvetica-Oblique", 42)
        c.drawCentredString(center_x, cursor_y, "Certificate")
        cursor_y -= 32

        c.setFont("Helvetica", 12)
        c.setFillColor(self.charcoal)
        c.drawCentredString(center_x, cursor_y, "OF PARTICIPATION")
        cursor_y -= 50

        c.setFont("Helvetica", 11)
        c.drawCentredString(center_x, cursor_y, "This certificate is awarded to :")
        cursor_y -= 45

        # Recipient name (uppercase, prominent)
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(self.deep_red)
        recipient = cert.get("name", " ").upper()
        # If recipient empty, draw a subtle placeholder underline instead of an empty string
        if recipient.strip():
            c.drawCentredString(center_x, cursor_y, recipient)
        else:
            # draw an underline placeholder of appropriate width
            line_w = 420
            c.setStrokeColor(self.deep_red)
            c.setLineWidth(1.2)
            c.line(center_x - line_w / 2, cursor_y - 6, center_x + line_w / 2, cursor_y - 6)
        cursor_y -= 45

        # Body paragraph
        body = cert.get("body", (
            "Celebrating outstanding accomplishment in the Dada Devs program. "
            "This recognizes proven mastery of open-source collaboration, Lightning innovation, "
            "and community impact across Web3 ecosystems."
        ))

        c.setFont("Helvetica", 10)
        c.setFillColor(self.charcoal)
        for line in self._wrap_lines(body, 75):
            c.drawCentredString(center_x, cursor_y, line)
            cursor_y -= 14
        cursor_y -= 20

        # Right dotted grid + QR with signature/metadata stacked
        grid_origin_x = content_right - 180
        grid_origin_y = 205

        c.setFillColor(self.gold_light)
        for col in range(9):
            for row in range(8):
                c.rect(grid_origin_x + col * 16, grid_origin_y + row * 16, 4, 4, fill=1, stroke=0)

        block_center = grid_origin_x + 72
        info_y = grid_origin_y + 170
        c.setFillColor(self.charcoal)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(block_center, info_y, "Signature (Ed25519)")
        info_y -= 12
        c.setFont("Helvetica", 8)
        signature_preview = cert.get("signature", "")[:28] if cert.get("signature") else ""
        c.drawCentredString(block_center, info_y, (signature_preview + "…") if signature_preview else "-")
        info_y -= 12
        c.setFont("Helvetica", 8)
        cert_id_preview = cert.get("id", "")[:20] if cert.get("id") else ""
        c.drawCentredString(block_center, info_y, (f"Certificate ID: {cert_id_preview}…") if cert_id_preview else "Certificate ID: -")
        info_y -= 12
        c.setFont("Helvetica-Bold", 8)
        cohort = cert.get("cohort", "-")
        issued_at = cert.get("issued_at", "-")
        c.drawCentredString(block_center, info_y, f"Cohort: {cohort}  |  Issued: {issued_at[:10]}")
        info_y -= 18
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(block_center, info_y, "Scan to verify on-chain proof")
        info_y -= 6
        c.setFont("Helvetica", 8)
        c.drawCentredString(block_center, info_y, "Bitcoin anchor + IPFS payload")

        # QR generation for verification URL
        verify_url = f"{self.base_url}/verify/{cert.get('id','') if cert.get('id') else ''}"
        qr = qrcode.QRCode(box_size=8, border=1)
        qr.add_data(verify_url)
        qr.make()
        qr_buffer = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)
        c.drawImage(qr_reader, grid_origin_x + 20, grid_origin_y + 20, width=110, height=110)

        # Signature lines (placeholders if no names provided)
        sig_y = 120
        sig_width = 190
        c.setStrokeColor(self.deep_red)
        c.setLineWidth(1.0)
        left_sig_x = content_left + 30
        right_sig_x = center_x + 60
        c.line(left_sig_x, sig_y, left_sig_x + sig_width, sig_y)
        c.line(right_sig_x, sig_y, right_sig_x + sig_width, sig_y)

        # Signatory text (no hard-coded personal names)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(self.charcoal)
        left_name = (left_signatory or "")
        right_name = (right_signatory or "DADA DEVS COUNCIL")
        c.drawCentredString(left_sig_x + sig_width / 2, sig_y - 16, (left_name.upper() if left_name else ""))
        c.setFont("Helvetica", 9)
        left_t = left_title or ""
        c.drawCentredString(left_sig_x + sig_width / 2, sig_y - 32, (left_t if left_t else ""))

        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(right_sig_x + sig_width / 2, sig_y - 16, (right_name.upper() if right_name else ""))
        c.setFont("Helvetica", 9)
        right_t = right_title or ""
        c.drawCentredString(right_sig_x + sig_width / 2, sig_y - 32, (right_t if right_t else ""))

        # Small muted provenance text
        c.setFont("Helvetica", 9)
        c.setFillColor(self.text_muted)
        c.drawString(content_left + 30, 110, "Secured with Ed25519 signatures, OpenTimestamps anchoring, and Bitcoin provenance.")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def _draw_polygon(c: canvas.Canvas, points: List[tuple], fill_color):
        path: PDFPathObject = c.beginPath()
        first = points[0]
        path.moveTo(*first)
        for x, y in points[1:]:
            path.lineTo(x, y)
        path.close()
        c.setFillColor(fill_color)
        c.drawPath(path, fill=1, stroke=0)

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

