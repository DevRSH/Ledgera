import re

def validar_rut_chileno(rut: str) -> str:
    """
    Valida y formatea un RUT chileno (algoritmo Módulo 11).
    Formatos aceptados: 12.345.678-9, 12345678-9, 123456789
    Retorna el RUT formateado: 12345678-9
    """
    # Limpiar puntos y guiones
    rut = rut.upper().replace(".", "").replace("-", "")
    
    if not re.match(r"^\d{7,8}[0-9K]$" , rut):
        raise ValueError("Formato de RUT inválido")
    
    cuerpo = rut[:-1]
    dv = rut[-1]
    
    # Calcular dígito verificador
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    
    dv_esperado = 11 - (suma % 11)
    if dv_esperado == 11:
        dv_esperado = "0"
    elif dv_esperado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(dv_esperado)
        
    if dv != dv_esperado:
        raise ValueError("Dígito verificador de RUT incorrecto")
    
    return f"{cuerpo}-{dv}"
