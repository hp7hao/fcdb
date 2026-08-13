#!/usr/bin/env python3
"""Preserve a displaced FCDB latest release under a contract-pinned tag."""

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


def contract_identity(manifest: dict[str, Any]) -> tuple[str, str]:
    schema = manifest.get("schema_version")
    if isinstance(schema, str) and SAFE_ID.fullmatch(schema):
        return schema, "schema"
    legacy = manifest.get("version")
    if isinstance(legacy, str) and SAFE_ID.fullmatch(legacy):
        return f"legacy-{legacy}", "contract"
    raise ValueError("stable version.json has neither schema_version nor a safe legacy version")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--candidate-schema", required=True)
    parser.add_argument("--asset", action="append", required=True)
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
            run("gh", "release", "download", f"{args.platform}-latest", "--pattern", asset, "--dir", temp)
        with zipfile.ZipFile(root / expected_main) as archive:
            manifest = json.loads(archive.read("version.json"))
        contract, channel_kind = contract_identity(manifest)
        if contract == args.candidate_schema:
            print(f"{args.platform}-latest already uses schema {contract}; no preservation needed")
            return 0

        tag = f"{args.platform}-{channel_kind}-{contract}"
        if run("gh", "release", "view", tag, check=False).returncode == 0:
            print(f"Previous stable contract already preserved: {tag}")
            return 0

        files = [str(root / asset) for asset in args.asset]
        run(
            "gh", "release", "create", tag, *files,
            "--title", f"{args.platform} database ({contract})",
            "--notes", f"Preserved {args.platform}-latest before promotion to schema {args.candidate_schema}.",
        )
        print(f"Preserved displaced stable contract: {tag}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
