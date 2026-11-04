#!/usr/bin/env python3
"""Audits historical Android14 PE libziparchive source only (no platform/recovery build)."""
from pathlib import Path
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]

def check(ok,msg):
    if not ok: raise AssertionError(msg)
    print("PASS historical source:",msg)

try:
    bp=(ROOT/"Android.bp").read_text()
    ziptool=(ROOT/"ziptool.cpp").read_text()
    archive=(ROOT/"zip_archive.cc").read_text()
    tests=json.loads((ROOT/"TEST_MAPPING").read_text())
    check('name: "libziparchive"' in bp and 'name: "libziparchive_for_incfs"' in bp,
          "legacy host/system/incfs library identities")
    check('name: "ziptool"' in bp and 'symlinks: ["unzip", "zipinfo"]' in bp,
          "legacy single ziptool global symlinks / old recovery change")
    check('name: "ziptool.recovery"' not in bp,
          "archive lacks AOSP17 explicit recovery ziptool binary")
    check('name: "ziparchive-tests"' in bp
          and 'name: "libziparchive_fuzzer"' in bp
          and 'name: "libziparchive_for_incfs_fuzzer"' in bp,
          "legacy tests and fuzz corpus declarations")
    check('StartsWith(name, "/")' in ziptool and 'StartsWith(name, "../")' in ziptool
          and 'name.find("/../")' in ziptool,
          "ZIP file-extraction path-traversal checks exist in archived tool")
    check('ZIPARCHIVE_DISABLE_CALLBACK_API' in archive,
          "legacy IncFS callback attack-surface gating marker")
    check(any(item.get("name") == "ziparchive-tests" for item in tests.get("presubmit", [])),
          "legacy ZIP regression test mapping")
    print("PASS historical archive source inventory ONLY: no AOSP17 aapt2/Soong, ZIP corpus or recovery image verified.")
except (AssertionError, OSError, json.JSONDecodeError) as e:
    print("FAIL:",e,file=sys.stderr)
    sys.exit(1)
