#!/usr/bin/env python3
"""config.APP_VERSION 기준으로 배포용 버전 문자열을 동기화합니다."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "src" / "kvocab_core" / "config.py"
PYPROJECT_PATH = ROOT / "pyproject.toml"
INFO_PATH = ROOT / "release" / "info.txt"
ISS_PATH = ROOT / "KVocabGuard.iss"

_VERSION_RE = re.compile(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
_PYPROJECT_VERSION_RE = re.compile(r'^(version\s*=\s*")[^"]+(")', re.MULTILINE)
_ISS_VERSION_RE = re.compile(r'(#define MyAppVersion ")[^"]+(")')


def _fail(msg: str) -> None:
    print(f"sync_version: {msg}", file=sys.stderr)
    sys.exit(1)


def read_config_version() -> str:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    m = _VERSION_RE.search(text)
    if not m:
        _fail(f"{CONFIG_PATH} 에서 APP_VERSION 을 찾을 수 없습니다.")
    return m.group(1)


def write_config_version(version: str) -> None:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    if not _VERSION_RE.search(text):
        _fail(f"{CONFIG_PATH} 에 APP_VERSION 할당이 없습니다.")
    text = _VERSION_RE.sub(f'APP_VERSION = "{version}"', text, count=1)
    CONFIG_PATH.write_text(text, encoding="utf-8")


def parse_version_tuple(version: str) -> tuple[int, int, int, int]:
    parts = version.strip().split(".")
    if not parts or not all(p.isdigit() for p in parts):
        _fail(f"버전 형식이 올바르지 않습니다: {version!r}")
    nums = [int(p) for p in parts]
    while len(nums) < 4:
        nums.append(0)
    if len(nums) > 4:
        _fail(f"버전은 최대 4자리까지 지원합니다: {version!r}")
    return nums[0], nums[1], nums[2], nums[3]


def render_info_txt(version: str) -> str:
    a, b, c, d = parse_version_tuple(version)
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({a}, {b}, {c}, {d}),
    prodvers=({a}, {b}, {c}, {d}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '041204b0',
        [StringStruct('CompanyName', 'Bae Gichan'),
        StringStruct('FileDescription', '한국어교육 단어 검사기'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'KVocabGuard'),
        StringStruct('LegalCopyright', 'Copyright (c) 2026 Bae Gichan'),
        StringStruct('OriginalFilename', 'KVocabGuard.exe'),
        StringStruct('ProductName', '한국어교육 단어 검사기'),
        StringStruct('ProductVersion', '{version}')])
      ]),
    VarFileInfo([VarStruct('Translation', [1042, 1200])])
  ]
)
"""


def sync_pyproject(version: str) -> None:
    text = PYPROJECT_PATH.read_text(encoding="utf-8")
    if not _PYPROJECT_VERSION_RE.search(text):
        _fail(f"{PYPROJECT_PATH} 에 version = 을 찾을 수 없습니다.")
    PYPROJECT_PATH.write_text(
        _PYPROJECT_VERSION_RE.sub(rf"\g<1>{version}\2", text), encoding="utf-8"
    )


def sync_info_txt(version: str) -> None:
    INFO_PATH.parent.mkdir(parents=True, exist_ok=True)
    INFO_PATH.write_text(render_info_txt(version), encoding="utf-8")


def sync_iss(version: str) -> None:
    if not ISS_PATH.exists():
        _fail(f"{ISS_PATH} 가 없습니다.")
    text = ISS_PATH.read_text(encoding="utf-8")
    if not _ISS_VERSION_RE.search(text):
        _fail(f"{ISS_PATH} 에 #define MyAppVersion 을 찾을 수 없습니다.")
    ISS_PATH.write_text(_ISS_VERSION_RE.sub(rf"\g<1>{version}\2", text), encoding="utf-8")


def read_iss_version() -> str:
    text = ISS_PATH.read_text(encoding="utf-8")
    m = _ISS_VERSION_RE.search(text)
    if not m:
        _fail(f"{ISS_PATH} 에 #define MyAppVersion 을 찾을 수 없습니다.")
    return m.group(0).split('"')[1]


def read_pyproject_version() -> str:
    text = PYPROJECT_PATH.read_text(encoding="utf-8")
    m = _PYPROJECT_VERSION_RE.search(text)
    if not m:
        _fail(f"{PYPROJECT_PATH} 에 version = 을 찾을 수 없습니다.")
    return m.group(0).split('"')[1]


def read_info_version() -> str:
    text = INFO_PATH.read_text(encoding="utf-8")
    m = re.search(r"StringStruct\('FileVersion', '([^']+)'\)", text)
    if not m:
        _fail("info.txt 에서 FileVersion 을 찾을 수 없습니다.")
    return m.group(1)


def sync_all(version: str) -> None:
    write_config_version(version)
    sync_pyproject(version)
    sync_info_txt(version)
    sync_iss(version)
    print(f"sync_version: {version} → config.py, pyproject.toml, release/info.txt, KVocabGuard.iss")


def check_all() -> None:
    expected = read_config_version()
    versions = {
        "config.py": expected,
        "pyproject.toml": read_pyproject_version(),
        "release/info.txt": read_info_version(),
        "KVocabGuard.iss": read_iss_version(),
    }
    bad = {k: v for k, v in versions.items() if v != expected}
    if bad:
        print("sync_version: 버전 불일치", file=sys.stderr)
        for k, v in sorted(versions.items()):
            mark = "OK" if v == expected else "!!"
            print(f"  [{mark}] {k}: {v}", file=sys.stderr)
        sys.exit(1)
    print(f"sync_version: OK (모두 {expected})")


def main() -> None:
    parser = argparse.ArgumentParser(description="KVocab Guard 배포 버전 동기화")
    parser.add_argument("--set", metavar="VERSION", help="버전 일괄 설정")
    parser.add_argument("--check", action="store_true", help="일치 여부만 검사")
    args = parser.parse_args()

    if args.check:
        check_all()
        return
    if args.set:
        sync_all(args.set.strip())
        return

    version = read_config_version()
    sync_pyproject(version)
    sync_info_txt(version)
    sync_iss(version)
    print(f"sync_version: config.APP_VERSION={version} → pyproject.toml, release/info.txt, KVocabGuard.iss")


if __name__ == "__main__":
    main()
