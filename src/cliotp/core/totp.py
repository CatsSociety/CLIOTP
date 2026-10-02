import hashlib
import hmac
import struct
import time

from cliotp.core.models import Account, decode_secret

_HASH = {"SHA1": hashlib.sha1, "SHA256": hashlib.sha256, "SHA512": hashlib.sha512}

# RFC 6238, apéndice B: t=59 s, 8 dígitos, (algoritmo, clave en ASCII, esperado)
RFC_VECTORS = [
    ("SHA1", b"12345678901234567890", "94287082"),
    ("SHA256", b"12345678901234567890123456789012", "46119246"),
    ("SHA512", b"1234567890123456789012345678901234567890123456789012345678901234", "90693936"),
]


def hotp(key: bytes, counter: int, digits: int = 6, algo: str = "SHA1") -> str:
    h = hmac.new(key, struct.pack(">Q", counter), _HASH[algo]).digest()
    o = h[-1] & 0x0F
    n = (struct.unpack(">I", h[o:o + 4])[0] & 0x7FFFFFFF) % 10**digits
    return str(n).zfill(digits)


def totp(acc: Account, t: float | None = None) -> str:
    t = time.time() if t is None else t
    return hotp(decode_secret(acc.secret), int(t // acc.period), acc.digits, acc.algo)


def remaining(acc: Account, t: float | None = None) -> int:
    t = time.time() if t is None else t
    return int(acc.period - t % acc.period)


def selftest() -> list[tuple[str, str, str]]:
    """Devuelve (algoritmo, esperado, obtenido) para cada vector del RFC."""
    return [(a, exp, hotp(k, 59 // 30, 8, a)) for a, k, exp in RFC_VECTORS]
