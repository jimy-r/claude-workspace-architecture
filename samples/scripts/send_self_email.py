"""Send a self-to-self email.

**Narrow Iron Law exception** — this script is the *only* path by which Claude
sends email autonomously, and it can *only* send to `<your-email>@example.com`. Any
other recipient raises ValueError. The `google-workspace` MCP remains scoped to
drafts (no `gmail.send`), preserving the broader Iron Law.

Intended use: daily morning-brief delivery to the user's own inbox. Do not call
this from other contexts without updating the Iron Law documentation.

Credentials: Gmail App Password resolved in this order:
  1. `GMAIL_APP_PASSWORD` environment variable (useful for one-off testing)
  2. OS keychain via `keyring` — service `morning-brief`, username `gmail-app-password`
     (on Windows this is the Credential Manager)

One-time user setup:
  1. Enable 2FA on Google account (already done per services-registry)
  2. Generate app password at https://myaccount.google.com/apppasswords — app
     name e.g. "Claude Morning Brief"
  3. Store in the keychain:
       python -c "import keyring; keyring.set_password('morning-brief', 'gmail-app-password', '<16-char-password>')"
  4. Also add a row in `Reference/services-registry.md` under Personal — AI / Development:
       "Gmail App Password (Morning Brief) | - | Self-to-self send for morning-brief orchestrator | ..."

Usage:
  python send_self_email.py --subject "..." --body "short body"
  python send_self_email.py --subject "..." --body-file path/to/body.txt
"""

from __future__ import annotations

import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

SELF_EMAIL = "<your-email>@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
KEYRING_SERVICE = "morning-brief"
KEYRING_USER = "gmail-app-password"


class SelfOnlyViolation(ValueError):
    """Raised if the script is ever asked to send to anyone other than SELF_EMAIL."""


def _require_self_recipient(to: str) -> None:
    if to.strip().lower() != SELF_EMAIL.lower():
        raise SelfOnlyViolation(
            f"Self-only sender — refusing recipient {to!r}. "
            f"This script can only send to {SELF_EMAIL}."
        )


def _resolve_app_password() -> str:
    pw = os.environ.get("GMAIL_APP_PASSWORD")
    if pw:
        return pw
    try:
        import keyring
    except ImportError as e:
        raise RuntimeError(
            "GMAIL_APP_PASSWORD not set and keyring module unavailable. "
            "Install keyring (pip install keyring) or set the env var."
        ) from e
    pw = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
    if not pw:
        raise RuntimeError(
            f"No password in keychain at service={KEYRING_SERVICE!r} user={KEYRING_USER!r}. "
            "Run: python -c \"import keyring; keyring.set_password('morning-brief', "
            "'gmail-app-password', '<app-password>')\""
        )
    return pw


def send_self(subject: str, body: str, to: str = SELF_EMAIL) -> None:
    """Send a plaintext email from SELF_EMAIL to SELF_EMAIL.

    Raises SelfOnlyViolation if `to` is not SELF_EMAIL.
    """
    _require_self_recipient(to)

    msg = EmailMessage()
    msg["From"] = SELF_EMAIL
    msg["To"] = SELF_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)

    password = _resolve_app_password()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.starttls()
        s.login(SELF_EMAIL, password)
        s.send_message(msg)


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--subject", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--body", help="Inline plaintext body")
    group.add_argument(
        "--body-file", type=Path, help="Path to a file with the plaintext body"
    )
    args = parser.parse_args()

    body = (
        args.body
        if args.body is not None
        else args.body_file.read_text(encoding="utf-8")
    )

    try:
        send_self(args.subject, body)
    except SelfOnlyViolation as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"send failed: {e}", file=sys.stderr)
        return 1
    print(f"sent: {args.subject}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
