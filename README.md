# cliotp

Gestor de códigos TOTP (RFC 6238) para la terminal, con bóveda cifrada
(scrypt + Fernet). Compatible con cualquier servicio que use 2FA tipo Google Authenticator.

## Instalación

```bash
sudo dnf install pipx                 # Fedora
pipx install git+https://github.com/USUARIO/cliotp.git
# desarrollo local (cambios al código se reflejan al instante):
pipx install --editable .
```

## Uso

```bash
cliotp                    # modo interactivo
cliotp --h                # ayuda
cliotp add GitHub:ana     # añade (el secreto se pide oculto)
cliotp add --uri          # pega una URI otpauth://
cliotp code github        # código actual (coincidencia parcial)
cliotp code github -c     # y lo copia al portapapeles
cliotp code github -q     # solo el código (útil en scripts)
cliotp watch              # todos los códigos en vivo
cliotp ls | rm | uri | selftest
```

Bóveda: `~/.local/share/cliotp/vault.bin` (permisos 600).
Cambia la ruta con `--vault RUTA` o `$CLIOTP_VAULT`.

## Estructura

```
src/cliotp/
├── core/      # lógica pura: Account, HOTP/TOTP, URIs otpauth
├── storage/   # cifrado y bóveda en disco
└── cli/       # argparse, comandos, modo interactivo
tests/         # pytest (vectores del RFC 6238, URIs, bóveda)
```

Dependencias en una sola dirección: `cli → storage → core`.

## Tests

```bash
pip install -e ".[dev]" && pytest
```

## Seguridad

- Los secretos nunca se pasan como argumento (quedarían en el historial y en `ps`).
- Sin la contraseña maestra la bóveda no se puede descifrar ni recuperar.
