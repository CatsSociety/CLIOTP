from urllib.parse import parse_qs, quote, unquote, urlparse

from cliotp.core.models import Account
from cliotp.errors import OtpError


def parse_uri(uri: str) -> Account:
    u = urlparse(uri.strip())
    if u.scheme != "otpauth" or u.netloc != "totp":
        raise OtpError("Solo se admiten URIs otpauth://totp/...")
    q = {k: v[0] for k, v in parse_qs(u.query).items()}
    if "secret" not in q:
        raise OtpError("La URI no incluye 'secret'.")
    label = unquote(u.path.lstrip("/"))
    issuer = q.get("issuer") or (label.split(":", 1)[0] if ":" in label else "")
    name = label or issuer
    if not name:
        raise OtpError("La URI no incluye etiqueta ni issuer.")
    try:
        digits, period = int(q.get("digits", 6)), int(q.get("period", 30))
    except ValueError:
        raise OtpError("digits/period inválidos en la URI.") from None
    return Account(name, q["secret"], digits, period, q.get("algorithm", "SHA1"), issuer)


def build_uri(acc: Account) -> str:
    qs = f"secret={acc.secret}&algorithm={acc.algo}&digits={acc.digits}&period={acc.period}"
    if acc.issuer:
        qs += f"&issuer={quote(acc.issuer)}"
    return f"otpauth://totp/{quote(acc.name)}?{qs}"
