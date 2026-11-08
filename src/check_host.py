"""Tiny demo: prepares a safe subprocess call. Not a web server."""

import subprocess


def check_host(hostname: str):
    # Pass arguments as a list; do not invoke a shell.
    return subprocess.run(
        ["ping", hostname],
        shell=False,
        capture_output=True,
        text=True,
    )
