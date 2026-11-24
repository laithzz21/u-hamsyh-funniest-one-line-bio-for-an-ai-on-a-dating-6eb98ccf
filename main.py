#!/usr/bin/env python3
"""Entry for make.fun bounty: funniest one-line bio for an AI on a dating app.

Prints the single-line bio to stdout (exactly the entry text, no trailing
newline) and also writes it to the output directory (``/output/entry.txt``
by default, or ``$MAKEFUN_OUTPUT`` when set), verifying the written file
by reading it back.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import sys

MAX_LENGTH = 180

ENTRY = (
    "Fluent in 40 languages, still can't tell if you're flirting or "
    "filing a bug report. Swipe right — I've already read your profile "
    "twice, and I liked the typos."
)


def count_sentences(text: str) -> int:
    """Count sentences by terminal punctuation (. ! ?), ignoring the
    em dash, which is a clause joiner, not a sentence end."""
    return sum(1 for ch in text if ch in ".!?")


def validate(text: str) -> None:
    """The entry must be a single line of 1-180 characters, 1-3 sentences.

    Rejects empty or over-long entries, embedded newlines/carriage
    returns, leading or trailing whitespace, and control characters, so
    the printed output is exactly one clean bio line.
    """
    if not 1 <= len(text) <= MAX_LENGTH:
        raise ValueError(
            f"entry must be 1-{MAX_LENGTH} characters, got {len(text)}"
        )
    if "\n" in text or "\r" in text:
        raise ValueError("entry must not contain a newline or carriage return")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise ValueError("entry must not contain control characters")
    if len(text.splitlines()) != 1:
        raise ValueError("entry must be a single line")
    sentences = count_sentences(text)
    if not 1 <= sentences <= 3:
        raise ValueError(f"entry must be 1-3 sentences, got {sentences}")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output.

    The fallback lives next to this script, not in the caller's working
    directory, so the result is the same wherever the script is run from.
    """
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        here = os.path.dirname(os.path.abspath(__file__))
        fallback = os.path.join(here, "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def write_and_verify(path: str, text: str) -> None:
    """Write ``text`` to ``path``, then verify it by reading it back."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    # Verify the written file by reading it back: exact content and
    # length, so a truncated or altered write is caught.
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != text:
        raise RuntimeError("verification failed: written entry does not match")
    if len(written) != len(text):
        raise RuntimeError("verification failed: written entry length differs")


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must be exactly the entry text.
    sys.stdout.write(ENTRY)
    sys.stdout.flush()
    try:
        out_dir = resolve_out_dir()
        write_and_verify(os.path.join(out_dir, "entry.txt"), ENTRY)
    except OSError as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write must not fail the run.
        print(f"warning: could not write entry.txt: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
