"""
Compression d'archives et fichiers génériques
Algorithmes : zstd (vitesse), lzma/xz (ratio), gzip, brotli
Pour les archives existantes (ZIP, 7Z, RAR...) : ré-archivage avec meilleure compression
"""

from pathlib import Path
import zipfile
import tarfile
import io
import os
import shutil
import tempfile

# Essai des imports optionnels
try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

import lzma
import gzip

# Profils : algo par défaut + niveau
ALGO_PROFILES = {
    "light":      {"algo": "zstd", "level": 3},
    "standard":   {"algo": "zstd", "level": 9},
    "aggressive": {"algo": "lzma", "level": 9},
}

# Extensions d'archives décompressables
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".bz2", ".tgz", ".tar.gz", ".tar.bz2"}


def compress_archive(
    input_path: Path,
    output_path: Path,
    level: str = "standard",
    algo: str = None,
    algo_level: int = None,
) -> Path:
    profile = ALGO_PROFILES.get(level, ALGO_PROFILES["standard"])
    target_algo = algo or profile["algo"]
    target_level = algo_level if algo_level is not None else profile["level"]

    ext = input_path.suffix.lower()
    is_zip = ext == ".zip"
    is_tar = ext in {".tar", ".tgz"} or input_path.name.endswith(".tar.gz") or input_path.name.endswith(".tar.bz2")

    # Si c'est une archive déjà compressée → ré-archiver les contenus
    if is_zip:
        return _recompress_zip(input_path, output_path, target_algo, target_level)
    elif is_tar:
        return _recompress_tar(input_path, output_path, target_algo, target_level)
    else:
        # Fichier brut → compresser directement
        return _compress_raw(input_path, output_path, target_algo, target_level)


def _compress_raw(input_path: Path, output_path: Path, algo: str, level: int) -> Path:
    data = input_path.read_bytes()

    if algo == "zstd" and HAS_ZSTD:
        cctx = zstd.ZstdCompressor(level=min(level, 22))
        compressed = cctx.compress(data)
        out = output_path.with_suffix(".zst")
        out.write_bytes(compressed)
        return out

    if algo == "brotli" and HAS_BROTLI:
        compressed = brotli.compress(data, quality=min(level, 11))
        out = output_path.with_suffix(".br")
        out.write_bytes(compressed)
        return out

    if algo == "lzma":
        preset = min(level, 9)
        compressed = lzma.compress(data, preset=preset)
        out = output_path.with_suffix(".xz")
        out.write_bytes(compressed)
        return out

    # Fallback : gzip
    out = output_path.with_suffix(".gz")
    with gzip.open(out, "wb", compresslevel=min(level, 9)) as f:
        f.write(data)
    return out


def _recompress_zip(input_path: Path, output_path: Path, algo: str, level: int) -> Path:
    """Extrait le ZIP et le ré-archive avec meilleure compression."""
    out = output_path.with_suffix(".zip")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Extraire
        with zipfile.ZipFile(input_path, "r") as zin:
            zin.extractall(tmpdir)

        # Ré-archiver avec compression maximale
        compress_type = zipfile.ZIP_DEFLATED
        compress_level = min(level, 9)

        with zipfile.ZipFile(out, "w", compression=compress_type, compresslevel=compress_level) as zout:
            tmppath = Path(tmpdir)
            for file in tmppath.rglob("*"):
                if file.is_file():
                    zout.write(file, file.relative_to(tmppath))

    return out


def _recompress_tar(input_path: Path, output_path: Path, algo: str, level: int) -> Path:
    """Extrait le TAR et le ré-archive en .tar.gz avec meilleure compression."""
    out = output_path.with_suffix("").with_suffix(".tar.gz")

    # Détecter le mode d'ouverture
    name = input_path.name.lower()
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        mode_r = "r:gz"
    elif name.endswith(".tar.bz2"):
        mode_r = "r:bz2"
    else:
        mode_r = "r:*"

    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(input_path, mode_r) as tin:
            tin.extractall(tmpdir)

        with tarfile.open(out, "w:gz", compresslevel=min(level, 9)) as tout:
            tmppath = Path(tmpdir)
            for file in tmppath.rglob("*"):
                if file.is_file():
                    tout.add(file, arcname=file.relative_to(tmppath))

    return out
