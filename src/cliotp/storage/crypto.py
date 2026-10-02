import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from cliotp.errors import VaultError


def _fernet(password: str, salt: bytes) -> Fernet:
    key = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(password.encode())
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt(password: str, salt: bytes, data: bytes) -> bytes:
    return _fernet(password, salt).encrypt(data)


def decrypt(password: str, salt: bytes, token: bytes) -> bytes:
    try:
        return _fernet(password, salt).decrypt(token)
    except InvalidToken:
        raise VaultError("Contraseña maestra incorrecta o bóveda corrupta.") from None
