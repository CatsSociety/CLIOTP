import pytest

from cliotp.core.totp import RFC_VECTORS, hotp, selftest


@pytest.mark.parametrize("algo,key,expected", RFC_VECTORS)
def test_rfc6238_vectors(algo, key, expected):
    assert hotp(key, 59 // 30, 8, algo) == expected


def test_selftest_all_ok():
    assert all(exp == got for _, exp, got in selftest())
