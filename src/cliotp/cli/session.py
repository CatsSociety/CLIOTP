import getpass
import sys

from cliotp.errors import VaultError
from cliotp.storage.vault import Vault


class Session:
    """Desbloquea la bóveda una sola vez y la mantiene en memoria."""

    def __init__(self, vault: Vault):
        self.vault = vault
        self._pw: str | None = None
        self._accounts = None

    def accounts(self) -> dict:
        if self._accounts is None:
            if self.vault.exists():
                pw = getpass.getpass("Contraseña maestra: ")
            else:
                print(f"Bóveda nueva en {self.vault.path}", file=sys.stderr)
                pw = getpass.getpass("Crea una contraseña maestra: ")
                if not pw:
                    raise VaultError("La contraseña no puede estar vacía.")
                if getpass.getpass("Repítela: ") != pw:
                    raise VaultError("Las contraseñas no coinciden.")
            self._accounts = self.vault.load(pw)
            self._pw = pw
        return self._accounts

    def save(self) -> None:
        self.vault.save(self._accounts, self._pw)
