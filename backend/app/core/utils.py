import re
from itertools import cycle

def validate_rut(rut: str) -> bool:
    """
    Validates a Chilean RUT (Rol Único Tributario).
    Format: 12345678-9 or 12.345.678-9
    """
    # Clean the RUT
    rut = rut.upper().replace(".", "").replace("-", "")
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False
    
    rut_body = rut[:-1]
    dv = rut[-1]
    
    # Calculate expected DV
    reversed_digits = map(int, reversed(rut_body))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    res = 11 - (s % 11)
    
    if res == 11:
        expected_dv = "0"
    elif res == 10:
        expected_dv = "K"
    else:
        expected_dv = str(res)
        
    return dv == expected_dv

def format_rut(rut: str) -> str:
    """
    Formats a RUT to XXXXXXXX-X format.
    """
    rut = rut.upper().replace(".", "").replace("-", "")
    if not rut:
        return ""
    return f"{rut[:-1]}-{rut[-1]}"
