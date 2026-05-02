import resend
from jinja2 import Environment, BaseLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.comunicacion import PlantillaEmail
from typing import Optional

if settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY

class EmailService:
    def _render_template(self, template_str: str, context: dict) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(template_str)
        return template.render(**context)

    async def _obtener_plantilla(self, db: AsyncSession, tenant_id: str, tipo: str) -> Optional[PlantillaEmail]:
        result = await db.execute(
            select(PlantillaEmail).filter(
                PlantillaEmail.tenant_id == tenant_id,
                PlantillaEmail.tipo == tipo
            )
        )
        return result.scalar_one_or_none()

    async def enviar_comprobante_pago(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        apoderado_email: str,
        apoderado_nombre: str,
        pdf_bytes: bytes,
        folio: str,
        mes_año: str,
        monto: int,
    ) -> str:
        """Sends a payment receipt via email."""
        plantilla = await self._obtener_plantilla(db, tenant_id, "comprobante_pago")
        
        asunto = "Comprobante de Pago - " + mes_año
        cuerpo = f"Hola {apoderado_nombre}, adjuntamos tu comprobante de pago folio {folio}."
        
        if plantilla:
            asunto = self._render_template(plantilla.asunto_template, {
                "mes_año": mes_año, "folio": folio
            })
            cuerpo = self._render_template(plantilla.cuerpo_html_template, {
                "apoderado_nombre": apoderado_nombre,
                "mes_año": mes_año,
                "monto": f"${monto:,.0f}".replace(",", "."),
                "folio": folio,
            })

        if not settings.RESEND_API_KEY:
            print(f"DEBUG: Email to {apoderado_email} would be sent here.")
            return "mock-id"

        params = {
            "from": f"Ledgera <noreply@resend.dev>", # Need verified domain for custom
            "to": [apoderado_email],
            "subject": asunto,
            "html": cuerpo,
            "attachments": [
                {
                    "filename": f"Comprobante-{folio}.pdf",
                    "content": list(pdf_bytes),
                }
            ],
        }
        
        response = resend.Emails.send(params)
        return response["id"]

email_service = EmailService()
