"""INTENTIONALLY INSECURE example. For static scanning ONLY; do not execute."""

import subprocess


def check_host(hostname: str):
    # Untrusted data goes into a shell command. A SAST rule should flag this.
    command = "ping " + hostname
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
