from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import qrcode
import base64
import io
import os

# Base directory for templates
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "pdf")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class PDFService:
    
    def generar_comprobante_pago(
        self,
        *,
        folio: str,
        alumno_nombre: str,
        apoderado_nombre: str,
        mes_año: str,
        monto: int,
        forma_pago: str,
        recibido_por: str,
        fecha: str,
        curso: str,
        colegio: str,
        qr_url: str,
    ) -> bytes:
        """Generates PDF for a payment receipt."""
        qr_b64 = self._generar_qr_base64(qr_url)
        template = jinja_env.get_template("comprobante_pago.html")
        html_content = template.render(
            folio=folio,
            alumno_nombre=alumno_nombre,
            apoderado_nombre=apoderado_nombre,
            mes_año=mes_año,
            monto=self._formatear_clp(monto),
            forma_pago=forma_pago,
            recibido_por=recibido_por,
            fecha=fecha,
            curso=curso,
            colegio=colegio,
            qr_base64=qr_b64,
        )
        return HTML(string=html_content).write_pdf()

    def _generar_qr_base64(self, url: str) -> str:
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def _formatear_clp(self, monto: int) -> str:
        return f"${monto:,.0f}".replace(",", ".")

pdf_service = PDFService()
