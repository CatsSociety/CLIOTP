import sys

from cliotp.cli import repl
from cliotp.cli.parser import build_parser
from cliotp.cli.session import Session
from cliotp.errors import OtpError
from cliotp.storage.vault import Vault, default_path


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    session = Session(Vault(args.vault or default_path()))
    try:
        func = getattr(args, "func", None)
        if func is None:
            session.accounts()  # pide la contraseña al entrar
            repl.run(parser, session)
        else:
            func(session, args)
    except OtpError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print(file=sys.stderr)
        return 130
    return 0
