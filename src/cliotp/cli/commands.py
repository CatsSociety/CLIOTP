import getpass
import sys

from cliotp.cli import clipboard, display
from cliotp.core.models import Account
from cliotp.core.totp import remaining, selftest, totp
from cliotp.core.uri import build_uri, parse_uri
from cliotp.errors import OtpError


def find(accounts: dict, text: str) -> Account:
    low = text.lower()
    exact = [n for n in accounts if n.lower() == low]
    if exact:
        return accounts[exact[0]]
    hits = [n for n in accounts if low in n.lower()]
    if len(hits) == 1:
        return accounts[hits[0]]
    if not hits:
        raise OtpError(f"Sin coincidencias para '{text}'.")
    raise OtpError("Ambiguo: " + ", ".join(sorted(hits)))


def cmd_ls(session, args):
    accounts = session.accounts()
    if not accounts:
        print("Bóveda vacía. Añade una con: cliotp add NOMBRE")
    for n in sorted(accounts):
        print(n)


def cmd_add(session, args):
    accounts = session.accounts()
    if args.uri:
        acc = parse_uri(getpass.getpass("URI otpauth:// (oculta): "))
        if args.name:
            acc.name = args.name
    else:
        if not args.name:
            raise OtpError("Falta el nombre. Uso: cliotp add NOMBRE  (o cliotp add --uri)")
        secret = getpass.getpass("Secreto base32 (oculto): ")
        acc = Account(args.name, secret, args.digits, args.period, args.algo)
    if acc.name in accounts and not args.force:
        raise OtpError(f"'{acc.name}' ya existe (usa --force para sobrescribir).")
    accounts[acc.name] = acc
    session.save()
    print(f"Añadida: {acc.name}")


def cmd_code(session, args):
    acc = find(session.accounts(), args.name)
    code = totp(acc)
    if args.quiet:
        print(code)
    else:
        print(f"{acc.name}: {display.spaced(code)}  ({remaining(acc)}s)")
    if args.copy:
        ok = clipboard.copy(code)
        print("Copiado al portapapeles." if ok else
              "No encontré wl-copy/xclip/xsel.", file=sys.stderr)


def cmd_watch(session, args):
    display.watch(session.accounts())


def cmd_rm(session, args):
    accounts = session.accounts()
    acc = find(accounts, args.name)
    if not args.yes and input(f"¿Borrar '{acc.name}'? (s/N) ").lower() != "s":
        print("Cancelado.")
        return
    del accounts[acc.name]
    session.save()
    print(f"Eliminada: {acc.name}")


def cmd_uri(session, args):
    print(build_uri(find(session.accounts(), args.name)))


def cmd_selftest(session, args):
    ok = True
    for algo, exp, got in selftest():
        good = exp == got
        ok &= good
        print(f"{algo:<7} {got}  {'OK' if good else 'FALLA (esperado ' + exp + ')'}")
    if not ok:
        raise OtpError("El autotest falló.")
