#!/usr/bin/env python3
"""Prepare the pinned, official Dipper XXL model and its T5 tokenizer.

Running this script without --check is an explicit download request (~45.07 GB
of model weights). It does not import torch, load a model, or allocate a GPU.
Only safetensors are downloaded; the tokenizer repository's weights are never
downloaded. --check is offline, read-only, and supports --tokenizer-only.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone


MODEL_REPO = "kalpeshk2011/dipper-paraphraser-xxl"
MODEL_REVISION = "c1fbf7a958a2aab022e9e6f81f7a3139f9e6ee3c"
TOKENIZER_REPO = "google/t5-v1_1-xxl"
TOKENIZER_REVISION = "3db67ab1af984cf10548a73467f0e5bca2aaaeb2"
BASELINE_DIR = Path(__file__).resolve().parent
MANIFEST_NAME = "prepare_manifest.json"


@dataclass(frozen=True)
class ExpectedFile:
    name: str
    size: int
    sha256: str | None = None
    git_blob_sha1: str | None = None


# Verified against the official HF /api/models/.../revision/<commit>?blobs=true.
# Both forms of weights exist upstream; deliberately select only safetensors.
MODEL_FILES = (
    ExpectedFile("config.json", 764,
                 git_blob_sha1="477b061259734430dd6fefcd8262e6d5c9a345ef"),
    ExpectedFile("model.safetensors.index.json", 53032,
                 git_blob_sha1="afdf64352fbeda4c604c4c013ecd6f931847a3cb"),
    ExpectedFile("model-00001-of-00005.safetensors", 9452262328,
                 sha256="cab17479f4b72774e9611831e18042d357a83a98eb9e805fe862d43759f92bdf"),
    ExpectedFile("model-00002-of-00005.safetensors", 9597007440,
                 sha256="67838dd1b5c440455fb8be6a4adb737ed52fa3281da449c04a1b9429a3f08dfb"),
    ExpectedFile("model-00003-of-00005.safetensors", 9955647024,
                 sha256="04a5e5b4753bd20df5d28226d99ceb0275a2baca1ad9c73a6de2eadac82da709"),
    ExpectedFile("model-00004-of-00005.safetensors", 9999712776,
                 sha256="af6f52908d164c3bd2a81c5aebadf200b71f89fea8b5216d21269273cda3993a"),
    ExpectedFile("model-00005-of-00005.safetensors", 6063154240,
                 sha256="7ad8f4816bb39248cdf333fa66352a2bf61b8c82921abbaaf943acc1fa72c530"),
)
TOKENIZER_FILES = (
    ExpectedFile("config.json", 593,
                 git_blob_sha1="5a439fe1a8c4a05c6b1e4bf6a11821b497bf0136"),
    ExpectedFile("special_tokens_map.json", 1786,
                 git_blob_sha1="881bdbffc06e471924ecea57f962bc5f8e2a9f21"),
    ExpectedFile("spiece.model", 791656,
                 git_blob_sha1="4e28ff6ebdf584f5372d9de68867399142435d9a"),
    ExpectedFile("tokenizer_config.json", 1857,
                 git_blob_sha1="b114c318caf72f6e89ea92e0755c41327a453198"),
)
REQUIRED_PACKAGES = (
    "huggingface-hub", "transformers", "sentencepiece", "nltk", "safetensors"
)


def package_versions() -> tuple[dict[str, str], list[str]]:
    versions, missing = {}, []
    for package in REQUIRED_PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            missing.append(package)
    return versions, missing


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    # Only called for small, non-LFS files (the largest is the 0.8 MB tokenizer).
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def inspect_files(directory: Path, expected_files: tuple[ExpectedFile, ...],
                  verify_hashes: bool = False) -> tuple[list[dict], list[str]]:
    observations, problems = [], []
    for expected in expected_files:
        path = directory / expected.name
        observed = {"expected": asdict(expected), "exists": path.is_file(),
                    "actual_size": None, "hash_verified": False}
        if not path.is_file():
            problems.append(f"missing file: {path}")
        else:
            observed["actual_size"] = path.stat().st_size
            if observed["actual_size"] != expected.size:
                problems.append(f"wrong size: {path} ({observed['actual_size']} != {expected.size})")
            elif expected.git_blob_sha1:
                observed["actual_git_blob_sha1"] = git_blob_sha1(path)
                observed["actual_sha256"] = file_sha256(path)
                observed["hash_verified"] = (
                    observed["actual_git_blob_sha1"] == expected.git_blob_sha1
                )
                if not observed["hash_verified"]:
                    problems.append(f"content does not match pinned official file: {path}")
            elif verify_hashes and expected.sha256:
                print(f"SHA256 checking {path.name} ({expected.size / 1e9:.2f} GB)...", flush=True)
                observed["actual_sha256"] = file_sha256(path)
                observed["hash_verified"] = observed["actual_sha256"] == expected.sha256
                if not observed["hash_verified"]:
                    problems.append(f"SHA256 mismatch: {path}")
        observations.append(observed)
    return observations, problems


def inspect_model_index(directory: Path) -> list[str]:
    index_path = directory / "model.safetensors.index.json"
    if not index_path.is_file():
        return [f"cannot check weight index: missing {index_path}"]
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        weight_map = index["weight_map"]
        if not isinstance(weight_map, dict) or not weight_map:
            return ["weight index has no nonempty weight_map"]
        referenced = set(weight_map.values())
        expected = {item.name for item in MODEL_FILES if item.sha256}
        if referenced != expected:
            return [f"weight index references unexpected or missing shards: {sorted(referenced ^ expected)}"]
        problems = []
        for name in sorted(referenced):
            # Names are fixed by the pinned manifest, so no index path traversal.
            if not (directory / name).is_file():
                problems.append(f"index references missing shard: {directory / name}")
        return problems
    except (KeyError, TypeError, ValueError, OSError) as error:
        return [f"invalid weight index {index_path}: {error}"]


def inspect_punkt(directory: Path) -> list[str]:
    try:
        import nltk
        nltk.data.path[:] = [str(directory)]
        nltk.data.find("tokenizers/punkt/english.pickle")
        nltk.data.find("tokenizers/punkt_tab/english/")
        sentences = nltk.sent_tokenize("A first sentence. A second sentence.", language="english")
        if len(sentences) != 2:
            return ["NLTK English sentence splitting did not pass the two-sentence check"]
        return []
    except (ImportError, LookupError, OSError, ValueError) as error:
        return [f"NLTK Punkt data is unavailable under {directory}: {str(error).splitlines()[0]}"]


def inspect_saved_provenance(directory: Path, repo: str, revision: str) -> list[str]:
    manifest_path = directory / MANIFEST_NAME
    if not manifest_path.is_file():
        print(f"Note: {manifest_path} is absent (manual download). Pinned small-file hashes, "
              "weight sizes, and index are checked; weight hashes require --verify-hashes.", flush=True)
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("repo_id") != repo or manifest.get("revision") != revision:
            return [f"download manifest has a different repository/revision: {manifest_path}"]
        return []
    except (ValueError, OSError) as error:
        return [f"invalid download manifest {manifest_path}: {error}"]


def check(args, versions: dict[str, str], missing_packages: list[str]) -> int:
    problems = [f"missing Python package: {name}" for name in missing_packages]
    print("Offline CPU-only check. No files will be written and no network is used.")
    print(f"Package versions: {json.dumps(versions, sort_keys=True)}")
    token_observations, token_problems = inspect_files(args.tokenizer_dir, TOKENIZER_FILES)
    problems.extend(token_problems)
    problems.extend(inspect_saved_provenance(args.tokenizer_dir, TOKENIZER_REPO, TOKENIZER_REVISION))
    model_observations = []
    if not args.tokenizer_only:
        model_observations, model_problems = inspect_files(
            args.model_dir, MODEL_FILES, args.verify_hashes
        )
        problems.extend(model_problems)
        problems.extend(inspect_model_index(args.model_dir))
        problems.extend(inspect_saved_provenance(args.model_dir, MODEL_REPO, MODEL_REVISION))
    if "nltk" not in missing_packages:
        problems.extend(inspect_punkt(args.nltk_dir))
    result = {
        "ok": not problems, "tokenizer_only": args.tokenizer_only,
        "model_dir": str(args.model_dir), "tokenizer_dir": str(args.tokenizer_dir),
        "nltk_dir": str(args.nltk_dir), "model_files": model_observations,
        "tokenizer_files": token_observations, "problems": problems,
        "weight_sha256_checked": bool(args.verify_hashes and not args.tokenizer_only),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if missing_packages:
        print("Install missing dependencies yourself, in the intended environment: "
              f"python -m pip install {' '.join(missing_packages)}", file=sys.stderr)
    return 0 if not problems else 1


def nearest_existing_parent(path: Path) -> Path:
    candidate = path
    while not candidate.exists() and candidate.parent != candidate:
        candidate = candidate.parent
    if not candidate.is_dir():
        candidate = candidate.parent
    return candidate


def missing_bytes(directory: Path, expected_files: tuple[ExpectedFile, ...]) -> int:
    # An incomplete/invalid final file is conservatively counted at full size.
    return sum(item.size for item in expected_files
               if not (directory / item.name).is_file()
               or (directory / item.name).stat().st_size != item.size)


def check_disk_space(directory: Path, expected_files: tuple[ExpectedFile, ...],
                     safety_margin: int, hash_invalid_bytes: int = 0) -> None:
    needed = missing_bytes(directory, expected_files) + hash_invalid_bytes
    available = shutil.disk_usage(nearest_existing_parent(directory)).free
    required = needed + safety_margin
    print(f"Disk check for {directory}: missing/invalid files {needed / 1e9:.3f} GB; "
          f"required with margin {required / 1e9:.3f} GB; free {available / 1e9:.3f} GB.", flush=True)
    if available < required:
        raise RuntimeError(f"insufficient free space for {directory}; need at least "
                           f"{required / 1e9:.2f} GB, have {available / 1e9:.2f} GB")


def atomic_json(path: Path, value: dict) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def download_repository(repo: str, revision: str, directory: Path,
                        expected_files: tuple[ExpectedFile, ...], args,
                        versions: dict[str, str]) -> None:
    from huggingface_hub import snapshot_download
    directory.mkdir(parents=True, exist_ok=True)
    # Force only corrupted finished files; other finished files and partial
    # downloads continue to use HF's local-dir incremental/resume metadata.
    observations, _ = inspect_files(directory, expected_files, args.verify_hashes)
    invalid_finished = [observation["expected"]["name"] for observation in observations
                        if observation["exists"] and (
                            observation["actual_size"] != observation["expected"]["size"]
                            or (observation["expected"]["git_blob_sha1"]
                                and not observation["hash_verified"])
                            or (args.verify_hashes and observation["expected"]["sha256"]
                                and not observation["hash_verified"]))]
    # A corrupt same-size finished file still occupies disk. Keep that file
    # recoverable while HF downloads its replacement, and reserve the entire
    # replacement size instead of counting zero missing bytes.
    same_size_invalid_bytes = sum(
        observation["expected"]["size"] for observation in observations
        if observation["expected"]["name"] in invalid_finished
        and observation["actual_size"] == observation["expected"]["size"]
    )
    check_disk_space(directory, expected_files,
                     5_000_000_000 if repo == MODEL_REPO else 100_000_000,
                     hash_invalid_bytes=same_size_invalid_bytes)
    if invalid_finished:
        print(f"Redownloading only invalid finished files: {invalid_finished}", flush=True)
        snapshot_download(repo_id=repo, revision=revision, local_dir=str(directory),
                          allow_patterns=invalid_finished, force_download=True,
                          max_workers=args.max_workers)
    snapshot_download(repo_id=repo, revision=revision, local_dir=str(directory),
                      allow_patterns=[item.name for item in expected_files],
                      max_workers=args.max_workers)
    observations, problems = inspect_files(directory, expected_files, args.verify_hashes)
    if repo == MODEL_REPO:
        problems.extend(inspect_model_index(directory))
    if problems:
        raise RuntimeError("download validation failed:\n" + "\n".join(problems))
    atomic_json(directory / MANIFEST_NAME, {
        "format_version": 1, "repo_id": repo, "revision": revision,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_repository_url": f"https://huggingface.co/{repo}/tree/{revision}",
        "hf_endpoint": os.environ.get("HF_ENDPOINT", "https://huggingface.co"),
        "download_api": "huggingface_hub.snapshot_download(local_dir, pinned revision)",
        "package_versions": versions, "files": observations,
        "weight_hashes_verified": bool(args.verify_hashes and repo == MODEL_REPO),
        "note": "Expected hashes are pinned upstream metadata; hash_verified records actual checks. "
                "Default weight checks verify sizes/index, not a full 45 GB SHA256 scan.",
    })


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model-dir", type=Path,
                        default=BASELINE_DIR / "models" / "dipper-paraphraser-xxl")
    parser.add_argument("--tokenizer-dir", type=Path,
                        default=BASELINE_DIR / "models" / "t5-v1_1-xxl-tokenizer")
    parser.add_argument("--nltk-dir", type=Path, default=BASELINE_DIR / "nltk_data")
    parser.add_argument("--check", action="store_true",
                        help="offline, read-only CPU checks; do not download or create directories")
    parser.add_argument("--tokenizer-only", action="store_true",
                        help="only prepare/check the small T5 tokenizer and NLTK Punkt data")
    parser.add_argument("--verify-hashes", action="store_true",
                        help="also read all ~45 GB of model shards to verify official SHA256 hashes")
    parser.add_argument("--max-workers", type=int, default=2,
                        help="parallel HF download workers (default: 2)")
    args = parser.parse_args(argv)
    if args.max_workers < 1:
        parser.error("--max-workers must be positive")
    for name in ("model_dir", "tokenizer_dir", "nltk_dir"):
        path = getattr(args, name).expanduser().resolve()
        if path == Path(path.anchor) or path == Path.home().resolve():
            parser.error(f"--{name.replace('_', '-')} must be a dedicated resource directory")
        setattr(args, name, path)
    if len({args.model_dir, args.tokenizer_dir, args.nltk_dir}) != 3:
        parser.error("model, tokenizer, and NLTK directories must be different")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    versions, missing_packages = package_versions()
    if args.check:
        return check(args, versions, missing_packages)
    if missing_packages:
        print(f"Missing dependencies: {', '.join(missing_packages)}. No downloads started.\n"
              f"Install them yourself: python -m pip install {' '.join(missing_packages)}",
              file=sys.stderr)
        return 1
    print(f"Pinned Dipper: {MODEL_REPO}@{MODEL_REVISION}")
    print(f"Pinned tokenizer only: {TOKENIZER_REPO}@{TOKENIZER_REVISION}")
    if not args.tokenizer_only:
        print("Model safetensors total: 45,067,783,808 bytes (~45.07 GB / 41.97 GiB).\n"
              "No .bin duplicates or tokenizer-repository model weights will be downloaded.", flush=True)
        check_disk_space(args.model_dir, MODEL_FILES, 5_000_000_000)
    check_disk_space(args.tokenizer_dir, TOKENIZER_FILES, 100_000_000)
    check_disk_space(args.nltk_dir, (), 100_000_000)
    # Respect existing, contradictory provenance instead of silently changing it.
    repositories = [(args.tokenizer_dir, TOKENIZER_REPO, TOKENIZER_REVISION)]
    if not args.tokenizer_only:
        repositories.append((args.model_dir, MODEL_REPO, MODEL_REVISION))
    for directory, repo, revision in repositories:
        if (directory / MANIFEST_NAME).is_file():
            problems = inspect_saved_provenance(directory, repo, revision)
            if problems:
                raise RuntimeError("\n".join(problems) + "; choose a new dedicated directory")
    download_repository(TOKENIZER_REPO, TOKENIZER_REVISION, args.tokenizer_dir,
                        TOKENIZER_FILES, args, versions)
    import nltk
    args.nltk_dir.mkdir(parents=True, exist_ok=True)
    nltk.data.path[:] = [str(args.nltk_dir)]
    if inspect_punkt(args.nltk_dir):
        for resource in ("punkt", "punkt_tab"):
            print(f"Preparing NLTK {resource} under {args.nltk_dir} ...", flush=True)
            if not nltk.download(resource, download_dir=str(args.nltk_dir), quiet=False,
                                 raise_on_error=True):
                raise RuntimeError(f"NLTK download failed: {resource}")
    problems = inspect_punkt(args.nltk_dir)
    if problems:
        raise RuntimeError("\n".join(problems))
    atomic_json(args.nltk_dir / MANIFEST_NAME, {
        "format_version": 1, "resources": ["punkt", "punkt_tab"],
        "language": "english", "nltk_version": versions["nltk"],
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": "NLTK resource names are recorded, not cryptographically version-pinned.",
    })
    if not args.tokenizer_only:
        download_repository(MODEL_REPO, MODEL_REVISION, args.model_dir,
                            MODEL_FILES, args, versions)
    args.check = True
    return check(args, versions, [])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
