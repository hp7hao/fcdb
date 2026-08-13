#!/usr/bin/env python3
"""Preserve a displaced FCDB latest release under a schema or unversioned tag."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def schema_identity(manifest: dict[str, Any]) -> str:
    schema = manifest.get("schema_version")
    if isinstance(schema, str) and SAFE_ID.fullmatch(schema):
        return schema
    return "unversioned"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, check=False, text=True, capture_output=True)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}: {detail}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--candidate-schema", required=True)
    parser.add_argument("--asset", action="append", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()

    for value, label in ((args.platform, "platform"), (args.candidate_schema, "candidate schema")):
        if not SAFE_ID.fullmatch(value):
            parser.error(f"unsafe {label}: {value}")
    expected_main = f"fcdb_{args.platform}.zip"
    if expected_main not in args.asset:
        parser.error(f"--asset must include {expected_main}")
    if any(not SAFE_ID.fullmatch(asset) for asset in args.asset):
        parser.error("asset names must contain only letters, digits, dot, underscore, or hyphen")

    with tempfile.TemporaryDirectory(prefix="fcdb-stable-") as temp:
        root = Path(temp)
        for asset in args.asset:
            run(
                "gh", "release", "download", f"{args.platform}-latest",
                "--repo", args.repository,
                "--pattern", asset,
                "--dir", temp,
            )
        with zipfile.ZipFile(root / expected_main) as archive:
            manifest = json.loads(archive.read("version.json"))
        schema = schema_identity(manifest)
        if schema == args.candidate_schema:
            print(f"{args.platform}-latest already uses schema {schema}; no preservation needed")
            return 0

        tag = f"{args.platform}-schema-{schema}" if schema != "unversioned" else f"{args.platform}-unversioned"
        if run("gh", "release", "view", tag, "--repo", args.repository, check=False).returncode == 0:
            print(f"Previous latest package already preserved: {tag}")
            return 0

        files = [str(root / asset) for asset in args.asset]
        run(
            "gh", "release", "create", tag, *files,
            "--repo", args.repository,
            "--title", f"{args.platform} database ({schema})",
            "--notes", f"Preserved {args.platform}-latest before promotion to schema {args.candidate_schema}.",
        )
        print(f"Preserved displaced latest package: {tag}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
