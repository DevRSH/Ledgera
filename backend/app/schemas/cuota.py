from pydantic import BaseModel
from typing import List, Literal

class EstadoDeuda(BaseModel):
    meses_configurados: int
    meses_pagados: int
    meses_condonados: int
    meses_adeudados: int
    monto_adeudado: int
    estado: Literal["al_dia", "debe_1_2", "debe_3_mas", "condonado_total"]
