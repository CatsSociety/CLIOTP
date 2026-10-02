import base64
import binascii
from dataclasses import asdict, dataclass, fields

from cliotp.errors import OtpError

ALGOS = ("SHA1", "SHA256", "SHA512")


def decode_secret(secret: str) -> bytes:
    s = secret.replace(" ", "").replace("-", "").upper()
    if not s:
        raise OtpError("El secreto está vacío.")
    try:
        return base64.b32decode(s + "=" * (-len(s) % 8))
    except (binascii.Error, ValueError):
        raise OtpError("Secreto base32 inválido.") from None


@dataclass
class Account:
    name: str
    secret: str
    digits: int = 6
    period: int = 30
    algo: str = "SHA1"
    issuer: str = ""

    def __post_init__(self):
        decode_secret(self.secret)  # valida
        self.secret = self.secret.replace(" ", "").replace("-", "").upper()
        self.algo = self.algo.upper()
        if self.algo not in ALGOS:
            raise OtpError(f"Algoritmo no soportado: {self.algo}")
        if not 6 <= self.digits <= 8:
            raise OtpError("digits debe estar entre 6 y 8.")
        if self.period <= 0:
            raise OtpError("period debe ser positivo.")

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("name")  # el nombre es la clave en la bóveda
        return d

    @classmethod
    def from_dict(cls, name: str, d: dict) -> "Account":
        known = {f.name for f in fields(cls)} - {"name"}
        return cls(name=name, **{k: v for k, v in d.items() if k in known})
