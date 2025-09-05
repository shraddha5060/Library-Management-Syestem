# auth.py
from datetime import date
import os
import hashlib
import binascii

# Try to use bcrypt if available, otherwise fallback to PBKDF2
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False

def hash_password(password: str) -> str:
    if HAS_BCRYPT:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return f"bcrypt${hashed.decode()}"
    else:
        # PBKDF2 fallback
        salt = hashlib.sha256(os.urandom(16)).hexdigest().encode()
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return f"pbkdf2${salt.decode()}${binascii.hexlify(dk).decode()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        method, rest = stored.split('$', 1)
    except Exception:
        return False
    if method == 'bcrypt' and HAS_BCRYPT:
        return bcrypt.checkpw(password.encode(), rest.encode())
    elif method == 'pbkdf2':
        salt, hexhash = rest.split('$')
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return binascii.hexlify(dk).decode() == hexhash
    return False
