class OtpError(Exception):
    """Error esperado y mostrable al usuario (sin traceback)."""


class VaultError(OtpError):
    """Problemas con la bóveda: contraseña, archivo corrupto, etc."""
