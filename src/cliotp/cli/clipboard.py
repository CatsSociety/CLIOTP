import shutil
import subprocess

_TOOLS = (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-ib"])


def copy(text: str) -> bool:
    """Copia al portapapeles (Wayland/X11). False si no hay herramienta."""
    for cmd in _TOOLS:
        if shutil.which(cmd[0]):
            subprocess.run(cmd, input=text.encode(), check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    return False
