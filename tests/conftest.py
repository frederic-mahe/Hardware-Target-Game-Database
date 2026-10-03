# -*- coding: utf-8 -*-
"""
Shared fixtures and helpers for the characterization test suite.

These tests are deliberately black-box: each script is driven through its
real command-line interface with ``subprocess`` and we assert on the
artifacts it produces (SMDB files, mismatch / missing reports, the resulting
directory tree, stdout and the exit code).  Nothing in the production scripts
is imported or modified, so the suite pins down *current* behaviour without
risking changes to it.
"""
import hashlib
import os
import subprocess
import sys
import zlib

import pytest

# Repository root = parent of this tests/ directory.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Make the repository's modules importable for in-process unit tests
# (the scripts are run via subprocess; shared helpers are imported directly).
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


@pytest.fixture
def repo_root():
    return REPO_ROOT


def run_script(script_name, args, cwd, env=None):
    """
    Run one of the repository's scripts via its CLI.

    Arguments:
      script_name - e.g. "parse_pack.py"
      args        - list of additional command-line arguments
      cwd         - working directory to run the script from (so that
                    relative paths in the output are deterministic)
      env         - optional dict of environment variables to overlay on top
                    of the current environment (e.g. to simulate a missing
                    optional dependency via PYTHONPATH). Defaults to the
                    current environment, unmodified.

    Returns a ``subprocess.CompletedProcess`` (stdout/stderr captured as text).
    """
    script_path = os.path.join(REPO_ROOT, script_name)
    # When measuring coverage (see .coveragerc / tests/README.md), the child
    # process is launched under `coverage run` so the script's execution is
    # recorded. Normal test runs are unaffected and need no coverage install.
    rcfile = os.environ.get("COVERAGE_PROCESS_START")
    if rcfile:
        cmd = [sys.executable, "-m", "coverage", "run",
               "--rcfile=" + rcfile, script_path] + list(args)
    else:
        cmd = [sys.executable, script_path] + list(args)
    run_env = None
    if env is not None:
        run_env = os.environ.copy()
        run_env.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=run_env,
    )


@pytest.fixture
def run():
    """Expose :func:`run_script` to tests."""
    return run_script


def write_tree(base, tree):
    """
    Materialise a nested dict as a directory tree under ``base``.

    Keys ending in "/" (or whose value is a dict) become directories; other
    keys become files whose content is the (str/bytes) value.  Example::

        write_tree(tmp_path, {
            "pack": {
                "USA": {"Sonic (USA).bin": "sonic-usa"},
                "readme.txt": "hi",
            },
        })
    """
    base = str(base)
    for name, value in tree.items():
        path = os.path.join(base, name)
        if isinstance(value, dict):
            os.makedirs(path, exist_ok=True)
            write_tree(path, value)
        else:
            os.makedirs(os.path.dirname(path) or base, exist_ok=True)
            data = value if isinstance(value, bytes) else value.encode("utf-8")
            with open(path, "wb") as handle:
                handle.write(data)


@pytest.fixture
def make_tree():
    return write_tree


def file_hashes(data):
    """Return the hashes parse_pack records for a blob of bytes."""
    if not isinstance(data, bytes):
        data = data.encode("utf-8")
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
        "crc": "{0:08x}".format(zlib.crc32(data) & 0xffffffff),
        "size": len(data),
    }


def smdb_line(relpath, data):
    """
    Build the exact SMDB line parse_pack emits for a file at ``relpath``
    containing ``data``.  ``relpath`` uses forward slashes (Unix format).
    """
    h = file_hashes(data)
    return "\t".join([
        h["sha256"],
        relpath,
        h["sha1"],
        h["md5"],
        h["crc"],
        str(h["size"]),
    ])


@pytest.fixture
def hashes():
    return file_hashes


@pytest.fixture
def line():
    return smdb_line
