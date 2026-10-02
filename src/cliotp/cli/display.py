import os
import select
import sys
import termios
import time
import tty

from cliotp.cli import clipboard
from cliotp.core.totp import remaining, totp

MAX_KEYS = 9  # cuentas seleccionables con una sola tecla (1-9)


def spaced(code: str) -> str:
    h = len(code) // 2
    return f"{code[:h]} {code[h:]}"


def _frame(names, accounts, width, status):
    lines = []
    for i, name in enumerate(names):
        a = accounts[name]
        r = remaining(a)
        key = str(i + 1) if i < MAX_KEYS else " "
        bar = "█" * (r * 20 // a.period)
        lines.append(f"[{key}] {name:<{width}}  {spaced(totp(a))}  {r:>2}s {bar}")
    lines.append(status or "    1-9 copiar código · q salir")
    return lines


def _copy(accounts, name) -> str:
    try:
        ok = clipboard.copy(totp(accounts[name]))
    except Exception:
        return "✘ No se pudo copiar"
    return f"✔ {name}: código copiado" if ok else "✘ Falta wl-copy / xclip / xsel"


def watch(accounts: dict) -> None:
    names = sorted(accounts)
    if not names:
        print("Bóveda vacía.")
        return
    out = sys.stdout
    height = len(names) + 1          # cuentas + línea de estado
    width = max(len(n) for n in names)
    interactive = sys.stdin.isatty()
    fd = sys.stdin.fileno() if interactive else None
    old = termios.tcgetattr(fd) if interactive else None
    status, until, drawn = "", 0.0, False
    try:
        if interactive:
            tty.setcbreak(fd)        # teclas al instante, sin eco; Ctrl+C sigue activo
        while True:
            if drawn:
                out.write(f"\033[{height}A")
            if status and time.time() > until:
                status = ""
            for line in _frame(names, accounts, width, status):
                out.write(f"\033[2K{line}\n")
            drawn = True
            out.flush()
            timeout = 1 - time.time() % 1   # redibuja justo al cambiar de segundo
            if not interactive:
                time.sleep(timeout)
                continue
            if select.select([fd], [], [], timeout)[0]:
                ch = os.read(fd, 1).decode(errors="ignore").lower()
                if ch == "q":
                    break
                if ch in "123456789" and ch and int(ch) <= min(len(names), MAX_KEYS):
                    status, until = _copy(accounts, names[int(ch) - 1]), time.time() + 3
    except KeyboardInterrupt:
        pass
    finally:
        if interactive:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        if drawn:
            out.write(f"\r\033[{height}A\033[J")  # borra todo el bloque
        out.flush()