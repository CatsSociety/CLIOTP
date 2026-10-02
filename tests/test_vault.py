import stat

import pytest

from cliotp.core.models import Account
from cliotp.errors import VaultError
from cliotp.storage.vault import Vault


def test_roundtrip_and_perms(tmp_path):
    v = Vault(tmp_path / "d" / "vault.bin")
    v.load("pw")
    v.save({"a": Account("a", "GEZDGNBVGY3TQOJQ")}, "pw")
    assert stat.S_IMODE(v.path.stat().st_mode) == 0o600
    got = Vault(v.path).load("pw")
    assert got["a"].secret == "GEZDGNBVGY3TQOJQ"


def test_wrong_password(tmp_path):
    v = Vault(tmp_path / "vault.bin")
    v.load("pw")
    v.save({}, "pw")
    with pytest.raises(VaultError):
        Vault(v.path).load("otra")
