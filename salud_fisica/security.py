"""Hash de contraseñas con sal usando la librería estándar.

Cubre el requerimiento no funcional de seguridad: las contraseñas se
almacenan como hash (PBKDF2-HMAC-SHA256), nunca en texto plano.
"""

import hashlib
import hmac
import secrets

_ITERATIONS = 200_000
_ALGO = "sha256"


def hash_password(password: str) -> str:
    """Genera un hash con sal aleatoria. Formato: pbkdf2$iteraciones$sal$hash."""
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(_ALGO, password.encode(), bytes.fromhex(salt), _ITERATIONS)
    return f"pbkdf2${_ITERATIONS}${salt}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verifica una contraseña contra el hash almacenado (comparación segura)."""
    try:
        _, iterations, salt, expected = stored.split("$")
        derived = hashlib.pbkdf2_hmac(_ALGO, password.encode(), bytes.fromhex(salt), int(iterations))
    except (ValueError, AttributeError):
        return False
    return hmac.compare_digest(derived.hex(), expected)
