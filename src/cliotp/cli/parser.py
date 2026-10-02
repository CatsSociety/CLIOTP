import argparse

from cliotp import __version__
from cliotp.cli import commands as c
from cliotp.core.models import ALGOS


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cliotp",
        description="Gestor de códigos TOTP en terminal. Sin subcomando abre el modo interactivo.",
    )
    p.add_argument("-V", "--version", action="version", version=f"cliotp {__version__}")
    p.add_argument("--vault", metavar="RUTA",
                   help="ruta de la bóveda (por defecto ~/.local/share/cliotp/vault.bin "
                        "o $CLIOTP_VAULT)")
    sub = p.add_subparsers(dest="command", metavar="COMANDO")

    def add(name, func, help_):
        sp = sub.add_parser(name, help=help_, description=help_)
        sp.set_defaults(func=func)
        return sp

    add("ls", c.cmd_ls, "lista las cuentas")

    sp = add("add", c.cmd_add, "añade una cuenta (el secreto se pide oculto)")
    sp.add_argument("name", nargs="?", help="nombre, ej. GitHub:usuario")
    sp.add_argument("--uri", action="store_true", help="pegar una URI otpauth:// en vez del secreto")
    sp.add_argument("--digits", type=int, default=6, choices=(6, 7, 8))
    sp.add_argument("--period", type=int, default=30)
    sp.add_argument("--algo", default="SHA1", type=str.upper, choices=ALGOS)
    sp.add_argument("--force", action="store_true", help="sobrescribir si ya existe")

    sp = add("code", c.cmd_code, "muestra el código actual de una cuenta")
    sp.add_argument("name", help="nombre o parte del nombre")
    sp.add_argument("-c", "--copy", action="store_true", help="copiar al portapapeles")
    sp.add_argument("-q", "--quiet", action="store_true", help="imprimir solo el código")

    add("watch", c.cmd_watch, "códigos en vivo: 1-9 copia el codigo, q sale de ese modo")

    sp = add("rm", c.cmd_rm, "elimina una cuenta")
    sp.add_argument("name")
    sp.add_argument("-y", "--yes", action="store_true", help="no pedir confirmación")

    sp = add("uri", c.cmd_uri, "muestra la URI otpauth:// de una cuenta (contiene el secreto)")
    sp.add_argument("name")

    add("selftest", c.cmd_selftest, "verifica el algoritmo con los vectores del RFC 6238")
    return p
