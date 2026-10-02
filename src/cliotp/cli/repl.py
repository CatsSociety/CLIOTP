import shlex

from cliotp import __version__
from cliotp.errors import OtpError


def run(parser, session) -> None:
    try:
        import readline  # noqa: F401  (historial y edición de línea)
    except ImportError:
        pass
    print(f"cliotp {__version__} — 'help' para ayuda, 'q' para salir.")
    while True:
        try:
            line = input("cliotp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        if line in ("q", "quit", "exit"):
            return
        if line == "help":
            parser.print_help()
            continue
        try:
            args = parser.parse_args(shlex.split(line))
        except SystemExit:  # argparse sale en errores y en --help
            continue
        except ValueError as e:
            print("Error:", e)
            continue
        func = getattr(args, "func", None)
        if func is None:
            continue
        try:
            func(session, args)
        except OtpError as e:
            print("Error:", e)
        except KeyboardInterrupt:
            print()
