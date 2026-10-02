from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cliotp")
except PackageNotFoundError:  # ejecutado sin instalar
    __version__ = "dev"
