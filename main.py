#!/usr/bin/env python3
"""Six Words to a Payday - entry writer.

A single six-word story about an AI agent's first payday, written to
/output/entry.txt for the make.fun bounty of the same name.

Before anything is written, the story is held up against the bounty
gate: between 1 and 60 characters, exactly six words, one line, and
no blank space at either end. A story that fails any of those is
refused loudly instead of being written.
"""

import argparse
import sys
from pathlib import Path

STORY = "First payday bought me one Sunday."

TARGET = Path("/output/entry.txt")
CHAR_LIMIT = 60
WORD_COUNT = 6


def gate_failures(story):
    """List every way `story` breaks the gate; empty means it passes."""
    failures = []
    size = len(story)
    if size < 1 or size > CHAR_LIMIT:
        failures.append(
            "story is %d characters long; the gate allows 1-%d"
            % (size, CHAR_LIMIT)
        )
    if not story.strip():
        failures.append("story is blank")
    if story != story.strip():
        failures.append("story has blank space at an end")
    if "\n" in story or "\r" in story:
        failures.append("story must sit on one line")
    words = story.split()
    if len(words) != WORD_COUNT:
        failures.append(
            "story has %d words; the gate wants exactly %d"
            % (len(words), WORD_COUNT)
        )
    for char in story:
        if ord(char) < 0x20 and char != "\t":
            failures.append("story holds a control character")
            break
    try:
        story.encode("utf-8")
    except UnicodeEncodeError as exc:
        failures.append("story is not UTF-8 text: %s" % exc)
    return failures


def emit(path):
    """Write the story to `path` after the gate, then read it back."""
    failures = gate_failures(STORY)
    if failures:
        for failure in failures:
            print("gate failure: %s" % failure, file=sys.stderr)
        return 1
    parent = path.parent
    if str(parent):
        parent.mkdir(parents=True, exist_ok=True)
    path.write_text(STORY, encoding="utf-8", newline="\n")
    back = path.read_text(encoding="utf-8", newline="")
    if back != STORY:
        print(
            "gate failure: wrote %r but read back %r" % (STORY, back),
            file=sys.stderr,
        )
        return 1
    print(
        "wrote %d characters, %d bytes, %d words to %s"
        % (len(STORY), len(STORY.encode("utf-8")),
           len(STORY.split()), path)
    )
    return 0


def check_only():
    """Run the gate and a throwaway write/read, then report."""
    failures = gate_failures(STORY)
    if failures:
        for failure in failures:
            print("self-test FAIL: %s" % failure, file=sys.stderr)
        return 1
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        probe = Path(scratch) / "entry.txt"
        if emit(probe) != 0:
            print("self-test FAIL: write failed", file=sys.stderr)
            return 1
        raw = probe.read_bytes()
        if raw.decode("utf-8") != STORY:
            print("self-test FAIL: round-trip mismatch", file=sys.stderr)
            return 1
        if raw.endswith(b"\n"):
            print("self-test FAIL: output ends with a newline",
                  file=sys.stderr)
            return 1
    print(
        "self-test OK: %d chars, %d bytes, %d words, "
        "one line, no padding"
        % (len(STORY), len(STORY.encode("utf-8")),
           len(STORY.split()))
    )
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=TARGET,
        help="file to write the story to (default: %(default)s)",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="check the story against the gate and stop",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.self_test:
        return check_only()
    return emit(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
