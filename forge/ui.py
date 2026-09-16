"""ANSI purple theme for forge CLI."""
import os, sys

_NO_COLOR = (
    os.environ.get("NO_COLOR")
    or not sys.stdout.isatty()
    or os.environ.get("FORGE_NO_COLOR") == "1"
)


def _c(code: str, s: str) -> str:
    return s if _NO_COLOR else f"\x1b[{code}m{s}\x1b[0m"


# 256-color purple ladder
def dim(s):     return _c("38;5;97",  s)   # muted purple
def soft(s):    return _c("38;5;140", s)   # lavender
def accent(s):  return _c("38;5;135", s)   # primary purple
def hot(s):     return _c("38;5;165", s)   # magenta-purple
def blood(s):   return _c("38;5;89",  s)   # deep purple-red
def bold(s):    return _c("1",        s)
def ok(s):      return _c("38;5;114", s)   # green
def warn(s):    return _c("38;5;179", s)   # amber
def err(s):     return _c("38;5;167", s)   # red

BANNER = r"""
    ███████╗ ██████╗ ██████╗  ██████╗ ███████╗    ██████╗ ████████╗
    ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝    ██╔══██╗╚══██╔══╝
    █████╗  ██║   ██║██████╔╝██║  ███╗█████╗      ██████╔╝   ██║
    ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝      ██╔══██╗   ██║
    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗    ██║  ██║   ██║
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝   ╚═╝
"""


def banner() -> str:
    return blood(BANNER)


def line(s: str = "") -> None:
    print(s)


def info(s: str) -> None:
    print(f"  {dim('·')} {s}")


def good(s: str) -> None:
    print(f"  {ok('✓')} {s}")


def bad(s: str) -> None:
    print(f"  {err('✗')} {s}")


def warn_(s: str) -> None:
    print(f"  {warn('!')} {s}")


def prompt_marker() -> str:
    return hot("▌")
