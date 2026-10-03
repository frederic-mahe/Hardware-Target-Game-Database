# -*- coding: utf-8 -*-
"""
Characterization tests for build_pack.py.

build_pack reads an SMDB, hashes every file under a source folder, and
reproduces the SMDB's directory layout in an output folder by copying /
hardlinking matching files (or extracting them out of zip archives).  It
reports coverage on stdout and can write a list of missing files.

Note: parse_database here splits each SMDB line into 5 columns
(sha256, path, sha1, md5, crc) and indexes files by BOTH their sha256 and
their crc, so the fixtures use full 6-column SMDB lines.
"""
import os
import struct
import zipfile
import py7zr


def write_db(path, lines):
    with open(str(path), "w") as handle:
        handle.write("\n".join(lines) + "\n")


def read(path):
    with open(str(path), "rb") as handle:
        return handle.read()


def test_copy_strategy_reproduces_layout(tmp_path, run, make_tree, line):
    make_tree(tmp_path, {"src": {"a.bin": "aaa", "b.bin": "bbb"}})
    db = tmp_path / "db.txt"
    write_db(db, [
        line("outpack/USA/a.bin", "aaa"),
        line("outpack/Japan/b.bin", "bbb"),
    ])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out),
                  "--file_strategy", "copy"],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert read(out / "outpack" / "USA" / "a.bin") == b"aaa"
    assert read(out / "outpack" / "Japan" / "b.bin") == b"bbb"
    assert "coverage: 2/2 (100.0%)" in result.stdout


def test_hardlink_strategy_shares_inode(tmp_path, run, make_tree, line):
    make_tree(tmp_path, {"src": {"a.bin": "aaa"}})
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/USA/a.bin", "aaa")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out),
                  "--file_strategy", "hardlink"],
                 cwd=tmp_path)

    assert result.returncode == 0
    src_file = tmp_path / "src" / "a.bin"
    dst_file = out / "outpack" / "USA" / "a.bin"
    assert os.path.samefile(str(src_file), str(dst_file))


def test_missing_file_reported_and_coverage(tmp_path, run, make_tree, line):
    make_tree(tmp_path, {"src": {"a.bin": "aaa"}})
    db = tmp_path / "db.txt"
    write_db(db, [
        line("outpack/USA/a.bin", "aaa"),
        line("outpack/USA/gone.bin", "gone"),
    ])
    out = tmp_path / "out"
    missing = tmp_path / "missing.txt"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out),
                  "-m", str(missing)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert read(out / "outpack" / "USA" / "a.bin") == b"aaa"
    assert not (out / "outpack" / "USA" / "gone.bin").exists()
    assert "coverage: 1/2 (50.0%)" in result.stdout
    assert "gone.bin" in missing.read_text()


def test_extract_from_zip_archive(tmp_path, run):
    # Build a zip whose entry's CRC we look up to drive the SMDB.
    src = tmp_path / "src"
    src.mkdir()
    zip_path = src / "games.zip"
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        zf.writestr("rom.bin", "rom-contents")
    with zipfile.ZipFile(str(zip_path)) as zf:
        crc = "{0:08x}".format(zf.getinfo("rom.bin").CRC & 0xffffffff)

    # crc lands in the 5th column; build_pack indexes by it and extracts.
    db = tmp_path / "db.txt"
    dummy_sha = "0" * 64
    dummy_other = "0" * 40
    dummy_md5 = "0" * 32
    write_db(db, ["\t".join([dummy_sha, "outpack/USA/rom.bin",
                             dummy_other, dummy_md5, crc, "12"])])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert read(out / "outpack" / "USA" / "rom.bin") == b"rom-contents"


def test_smart_strategy_hardlinks_duplicates(tmp_path, run, make_tree, line):
    # One source file maps to two destinations with the same hash: the first
    # is copied, the second is hardlinked to that first copy.
    make_tree(tmp_path, {"src": {"dup.bin": "dup"}})
    db = tmp_path / "db.txt"
    write_db(db, [
        line("outpack/USA/a.bin", "dup"),
        line("outpack/USA/b.bin", "dup"),
    ])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out),
                  "--file_strategy", "smart"],
                 cwd=tmp_path)

    assert result.returncode == 0
    first = out / "outpack" / "USA" / "a.bin"
    second = out / "outpack" / "USA" / "b.bin"
    assert read(first) == b"dup"
    assert read(second) == b"dup"
    assert os.path.samefile(str(first), str(second))


def test_existing_file_overwritten_without_skip(tmp_path, run, make_tree,
                                                line):
    make_tree(tmp_path, {
        "src": {"a.bin": "aaa"},
        "out": {"outpack": {"USA": {"a.bin": "stale"}}},
    })
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/USA/a.bin", "aaa")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    # Without --skip_existing the stale file is replaced.
    assert read(out / "outpack" / "USA" / "a.bin") == b"aaa"


def test_drop_initial_directory(tmp_path, run, make_tree, line):
    make_tree(tmp_path, {"src": {"a.bin": "aaa"}})
    db = tmp_path / "db.txt"
    write_db(db, [line("topdir/USA/a.bin", "aaa")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out), "-x"],
                 cwd=tmp_path)

    assert result.returncode == 0
    # The leading "topdir/" component is dropped from the output layout.
    assert read(out / "USA" / "a.bin") == b"aaa"
    assert not (out / "topdir").exists()


def test_creates_missing_empty_file(tmp_path, run, make_tree, line):
    # An SMDB entry for an empty file that is absent from the source is
    # recreated as an empty file. The empty sub-folder exercises the
    # "directory with no files" walk branch.
    make_tree(tmp_path, {"src": {"keep.bin": "x", "sub": {}}})
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/empty.bin", "")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    empty = out / "outpack" / "empty.bin"
    assert empty.exists()
    assert empty.stat().st_size == 0


def test_existing_empty_target_overwritten_without_skip(tmp_path, run,
                                                        make_tree, line):
    # The empty-file target already exists with content; without
    # --skip_existing it is removed and recreated empty.
    make_tree(tmp_path, {
        "src": {"keep.bin": "x"},
        "out": {"outpack": {"empty.bin": "stale-content"}},
    })
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/empty.bin", "")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert (out / "outpack" / "empty.bin").stat().st_size == 0


def test_existing_empty_target_kept_with_skip(tmp_path, run, make_tree, line):
    # With --skip_existing the pre-existing target is left untouched.
    make_tree(tmp_path, {
        "src": {"keep.bin": "x"},
        "out": {"outpack": {"empty.bin": "stale-content"}},
    })
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/empty.bin", "")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out), "-s"],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert read(out / "outpack" / "empty.bin") == b"stale-content"


def test_zip_with_extra_entries_skips_nonmatching(tmp_path, run):
    src = tmp_path / "src"
    src.mkdir()
    zip_path = src / "games.zip"
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        zf.writestr("rom.bin", "rom-contents")
        zf.writestr("other.bin", "other-contents")
    with zipfile.ZipFile(str(zip_path)) as zf:
        crc = "{0:08x}".format(zf.getinfo("rom.bin").CRC & 0xffffffff)

    db = tmp_path / "db.txt"
    write_db(db, ["\t".join(["0" * 64, "outpack/rom.bin",
                             "0" * 40, "0" * 32, crc, "12"])])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    # Only the targeted entry is extracted; the other zip member is skipped.
    assert read(out / "outpack" / "rom.bin") == b"rom-contents"
    assert not (out / "outpack" / "other.bin").exists()


def test_corrupt_zip_is_reported_but_not_fatal(tmp_path, run, line):
    # A file that looks like a zip (valid end-of-central-directory record) but
    # cannot actually be opened triggers the "attempted to parse as a zip"
    # warning; the run still completes successfully.
    src = tmp_path / "src"
    src.mkdir()
    eocd = b"PK\x05\x06" + struct.pack("<HHHHIIH", 0, 0, 1, 1, 46, 0, 0)
    (src / "corrupt.zip").write_bytes(b"not-a-real-local-header" + eocd)
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/USA/unrelated.bin", "unrelated")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert "as a zip archive" in result.stdout


def test_corrupt_7z_is_reported_but_not_fatal(tmp_path, run, line):
    # A file with a genuine 7z magic number but garbage after it triggers
    # the "failed to read as a 7z archive" warning; the run still
    # completes successfully.
    src = tmp_path / "src"
    src.mkdir()
    magic = b"7z\xbc\xaf\x27\x1c"
    (src / "corrupt.7z").write_bytes(magic + b"not-a-real-header")
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/USA/unrelated.bin", "unrelated")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert "as a 7z archive" in result.stdout


def test_extract_from_7z_archive(tmp_path, run):
    src = tmp_path / "src"
    src.mkdir()
    sz_path = src / "games.7z"
    rom_file = tmp_path / "rom.bin"
    rom_file.write_bytes(b"7z-rom-contents")
    with py7zr.SevenZipFile(str(sz_path), "w") as szf:
        szf.write(str(rom_file), arcname="rom.bin")
    with py7zr.SevenZipFile(str(sz_path)) as szf:
        crc = "{0:08x}".format(szf.getinfo("rom.bin").crc32)

    db = tmp_path / "db.txt"
    write_db(db, ["\t".join(["0" * 64, "outpack/rom.bin",
                             "0" * 40, "0" * 32, crc, "15"])])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert read(out / "outpack" / "rom.bin") == b"7z-rom-contents"


def test_extract_from_zip_and_7z(tmp_path, run):
    # Source folder contains both a zip and a 7z archive
    src = tmp_path / "src"
    src.mkdir()

    zip_path = src / "games.zip"
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        zf.writestr("zip-rom.bin", "zip-rom-contents")
    with zipfile.ZipFile(str(zip_path)) as zf:
        zip_crc = "{0:08x}".format(zf.getinfo("zip-rom.bin").CRC & 0xffffffff)

    sz_path = src / "games.7z"
    rom_file = tmp_path / "rom.bin"
    rom_file.write_bytes(b"7z-rom-contents")
    with py7zr.SevenZipFile(str(sz_path), "w") as szf:
        szf.write(str(rom_file), arcname="7z-rom.bin")
    with py7zr.SevenZipFile(str(sz_path)) as szf:
        sz_crc = "{0:08x}".format(szf.getinfo("7z-rom.bin").crc32)

    db = tmp_path / "db.txt"
    write_db(db, [
        "\t".join(["0" * 64, "outpack/zip-rom.bin",
                   "0" * 40, "0" * 32, zip_crc, "16"]),
        "\t".join(["0" * 64, "outpack/7z-rom.bin",
                   "0" * 40, "0" * 32, sz_crc, "15"]),
    ])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert read(out / "outpack" / "zip-rom.bin") == b"zip-rom-contents"
    assert read(out / "outpack" / "7z-rom.bin") == b"7z-rom-contents"


def test_missing_py7zr_treats_7z_as_ordinary_file(tmp_path, run, line):
    # Simulate py7zr not being installed using a stub module that fails to
    # import, earlier on PYTHONPATH than the real package. build_pack.py should
    # behave exactly as it did prior to 7z support: a .7z file is simply not
    # recognized as an archive.
    stub_dir = tmp_path / "stub_py7zr"
    stub_dir.mkdir()
    (stub_dir / "py7zr.py").write_text(
        "raise ImportError('py7zr intentionally unavailable for this test')\n")

    src = tmp_path / "src"
    src.mkdir()
    magic = b"7z\xbc\xaf\x27\x1c"
    (src / "games.7z").write_bytes(magic + b"not-really-parsed")

    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/USA/unrelated.bin", "unrelated")])
    out = tmp_path / "out"

    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    pythonpath = str(stub_dir)
    if existing_pythonpath:
        pythonpath += os.pathsep + existing_pythonpath

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path,
                 env={"PYTHONPATH": pythonpath})

    assert result.returncode == 0
    assert "7z" not in result.stdout
    assert "coverage: 0/1 (0.0%)" in result.stdout


def test_missing_file_without_report_flag(tmp_path, run, make_tree, line):
    make_tree(tmp_path, {"src": {"a.bin": "aaa"}})
    db = tmp_path / "db.txt"
    write_db(db, [
        line("outpack/USA/a.bin", "aaa"),
        line("outpack/USA/gone.bin", "gone"),
    ])
    out = tmp_path / "out"

    # No -m flag: the missing file is reflected in coverage but no report
    # file is written.
    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out)],
                 cwd=tmp_path)

    assert result.returncode == 0
    assert "coverage: 1/2 (50.0%)" in result.stdout


def test_skip_existing_leaves_file_untouched(tmp_path, run, make_tree, line):
    make_tree(tmp_path, {
        "src": {"a.bin": "aaa"},
        "out": {"outpack": {"USA": {"a.bin": "preexisting"}}},
    })
    db = tmp_path / "db.txt"
    write_db(db, [line("outpack/USA/a.bin", "aaa")])
    out = tmp_path / "out"

    result = run("build_pack.py",
                 ["-i", "src", "-d", str(db), "-o", str(out),
                  "-s"],
                 cwd=tmp_path)

    assert result.returncode == 0
    # With --skip_existing the pre-existing file is not overwritten.
    assert read(out / "outpack" / "USA" / "a.bin") == b"preexisting"
