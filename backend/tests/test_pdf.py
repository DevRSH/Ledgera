import pytest
from app.services.pdf_service import pdf_service

def test_generar_comprobante_pdf_valido():
    pdf_bytes = pdf_service.generar_comprobante_pago(
        folio="2026-TEST-001",
        alumno_nombre="Juan Perez",
        apoderado_nombre="Maria Garcia",
        mes_año="Marzo 2026",
        monto=25000,
        forma_pago="Transferencia",
        recibido_por="Tesorero 1",
        fecha="2026-05-01",
        curso="5to Básico B",
        colegio="Colegio Example",
        qr_url="https://tesoapp.cl/verify/2026-TEST-001"
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF starts with %PDF
    assert pdf_bytes.startswith(b"%PDF")
