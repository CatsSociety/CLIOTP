import json
import os
from pathlib import Path

from cliotp.core.models import Account
from cliotp.errors import VaultError
from cliotp.storage import crypto

SALT_LEN = 16


def default_path() -> Path:
    if env := os.environ.get("CLIOTP_VAULT"):
        return Path(env)
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "cliotp" / "vault.bin"


class Vault:
    """Archivo: salt (16 B) + token Fernet con un JSON {nombre: cuenta}."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._salt: bytes | None = None

    def exists(self) -> bool:
        return self.path.exists()

    def load(self, password: str) -> dict[str, Account]:
        if not self.exists():
            self._salt = os.urandom(SALT_LEN)
            return {}
        raw = self.path.read_bytes()
        if len(raw) <= SALT_LEN:
            raise VaultError("Bóveda corrupta.")
        self._salt = raw[:SALT_LEN]
        data = json.loads(crypto.decrypt(password, self._salt, raw[SALT_LEN:]))
        return {n: Account.from_dict(n, d) for n, d in data.items()}

    def save(self, accounts: dict[str, Account], password: str) -> None:
        if self._salt is None:
            raise VaultError("La bóveda no se ha cargado.")
        payload = json.dumps({n: a.to_dict() for n, a in accounts.items()}).encode()
        token = crypto.encrypt(password, self._salt, payload)
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        tmp = self.path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(self._salt + token)
        os.replace(tmp, self.path)
