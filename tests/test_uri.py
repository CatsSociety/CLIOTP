import pytest

from cliotp.core.uri import build_uri, parse_uri
from cliotp.errors import OtpError

URI = "otpauth://totp/GitHub:ana?secret=GEZDGNBVGY3TQOJQ&issuer=GitHub&digits=8&period=60"


def test_parse():
    a = parse_uri(URI)
    assert (a.name, a.issuer, a.digits, a.period, a.algo) == ("GitHub:ana", "GitHub", 8, 60, "SHA1")


def test_roundtrip():
    a = parse_uri(URI)
    assert parse_uri(build_uri(a)) == a


@pytest.mark.parametrize("bad", ["http://x", "otpauth://hotp/x?secret=AAAA", "otpauth://totp/x"])
def test_invalid(bad):
    with pytest.raises(OtpError):
        parse_uri(bad)
