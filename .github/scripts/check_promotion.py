#!/usr/bin/env python3
"""Gate stable FCDB channels without claiming downstream compatibility."""

from __future__ import annotations

import argparse
import re
import sys

SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
UNVERSIONED = "unversioned"
PLATFORMS = {"pico8", "pyxel", "pyxelpico"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    parser.add_argument("--candidate-schema", required=True)
    parser.add_argument("--latest-schema", required=True)
    parser.add_argument("--candidate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SEMVER.fullmatch(args.candidate_schema):
        print(
            f"candidate schema must use Semantic Versioning: {args.candidate_schema}",
            file=sys.stderr,
        )
        return 2
    if not (SEMVER.fullmatch(args.latest_schema) or args.latest_schema == UNVERSIONED):
        print(
            f"latest schema must be a schema version or unversioned: {args.latest_schema}",
            file=sys.stderr,
        )
        return 2

    channel = f"{args.platform}-latest"
    versions_match = args.candidate_schema == args.latest_schema
    if args.candidate_only:
        if versions_match:
            print(
                f"Candidate-only publication is invalid because {channel} already allows "
                f"schema {args.candidate_schema}",
                file=sys.stderr,
            )
            return 1
        print(
            f"Candidate validation allowed without publication: {args.platform} schema "
            f"{args.candidate_schema}; {channel} remains {args.latest_schema}"
        )
        return 0

    if versions_match:
        print(f"Stable promotion allowed: {channel} schema {args.candidate_schema}")
        return 0

    print(
        f"Stable promotion blocked: {channel} schema is {args.latest_schema}, "
        f"candidate is {args.candidate_schema}. Keep the locally generated candidate "
        "unpublished and run each downstream consumer's own full FCDB package suite. After reviewing "
        "that evidence, the release owner authorizes cutover by updating the checked-in "
        "latest schema.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
