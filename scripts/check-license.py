#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check that LICENSE is still the Apache License 2.0, word for word.

The appendix at the end of the license is Apache's template: its copyright
line may be left as the placeholder or filled in with the copyright holder, so
that one line is normalised before hashing. Everything else has to match
apache.org's LICENSE-2.0.txt exactly.

Run it directly:

    python3 scripts/check-license.py

If you ever *deliberately* change the license text, update EXPECTED_SHA256.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

# sha256 of the normalised canonical text (see normalise() below)
EXPECTED_SHA256 = "53cd3a09cf95d164718c7358ef681fc59ff2cff1cb1f16463e84069620801e40"

LICENSE = pathlib.Path("LICENSE")

# only the example line in the appendix starts with "Copyright"
COPYRIGHT_LINE = re.compile(r"^\s*Copyright\s+\S.*$")
COPYRIGHT_PLACEHOLDER = "   Copyright [yyyy] [name of copyright owner]"

REQUIRED = [
    "Apache License",
    "Version 2.0, January 2004",
    "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION",
    "1. Definitions.",
    "2. Grant of Copyright License.",
    "3. Grant of Patent License.",
    "4. Redistribution.",
    "5. Submission of Contributions.",
    "6. Trademarks.",
    "7. Disclaimer of Warranty.",
    "8. Limitation of Liability.",
    "9. Accepting Warranty or Additional Liability.",
]


def normalise(text: str) -> str:
    """Drop differences that carry no meaning: CRLF, trailing spaces, blank
    lines at either end, and whatever the appendix copyright line says."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip() for line in lines]

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    lines = [
        "   Copyright <holder>" if COPYRIGHT_LINE.match(line) else line
        for line in lines
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    if not LICENSE.is_file():
        print("error: LICENSE is missing", file=sys.stderr)
        return 1

    raw = LICENSE.read_text(encoding="utf-8")
    text = normalise(raw)

    problems = [f"missing: {needle}" for needle in REQUIRED if needle not in text]

    appendix = [
        line for line in text.split("\n") if line.startswith("   Copyright ")
    ]
    if not appendix:
        problems.append("missing the appendix copyright line")

    digest = hashlib.sha256(text.encode()).hexdigest()
    if digest != EXPECTED_SHA256:
        problems.append(
            "text differs from the canonical Apache-2.0 license "
            f"(normalised sha256 is {digest})"
        )

    if problems:
        print("LICENSE is not the unmodified Apache License 2.0:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(
            "\nRestore the text from https://www.apache.org/licenses/LICENSE-2.0.txt "
            "or, if the change was deliberate, update EXPECTED_SHA256 in "
            "scripts/check-license.py.",
            file=sys.stderr,
        )
        return 1

    print(
        f"LICENSE matches the canonical Apache License 2.0 "
        f"({len(raw.encode('utf-8'))} bytes)"
    )
    if COPYRIGHT_PLACEHOLDER not in raw:
        print("note: the appendix copyright line is filled in")
    return 0


if __name__ == "__main__":
    sys.exit(main())
