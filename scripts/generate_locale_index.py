#!/usr/bin/env python3
"""
Rebuilds blog index trees and updates _meta.json for all supported locales:
- blog-en-index-tree.json
- blog-hi-index-tree.json
- blog-ne-index-tree.json
- _meta.json (Master multilingual index)
- _multilang_meta.json

Usage:
  python3 scripts/generate_locale_index.py
      Full rebuild from every file under en/, hi/ and ne/.
  python3 scripts/generate_locale_index.py --roots 22_Home_Living 23_Interior_Design
      Refresh only the entries under the named top-level folders (added, retitled, new
      locales, removed files) and keep every other entry exactly as it is in the committed
      indexes. Re-running it is safe: the output only depends on the files on disk and on the
      entries outside the roots. Output order is the full rebuild's order.
  Add --tracked-only to skip files git does not track yet (translations still being written).
"""

import argparse
import os
import json
import re
from pathlib import Path, PurePosixPath

ROOT_DIR = Path(__file__).resolve().parent.parent

LOCALES = ["en", "hi", "ne"]

def extract_frontmatter(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n([\s\S]*?)\n---", content)
        if not match:
            return {}
        
        raw_yaml = match.group(1)
        meta = {}
        for line in raw_yaml.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("-") and not line.startswith("#"):
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip().strip("'\"")
        return meta
    except Exception:
        return {}

def tracked_files(root: Path):
    """Markdown paths (relative, posix) that git tracks or has staged under the locale folders."""
    import subprocess

    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *LOCALES],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")
    return {p for p in out.split("\0") if p}


def scan_locale_tree(locale: str, root: Path = ROOT_DIR, roots=None, tracked=None):
    locale_dir = root / locale
    if not locale_dir.exists():
        return []

    if roots is None:
        files = locale_dir.glob("**/*.md*")
    else:
        files = [f for r in roots if (locale_dir / r).is_dir() for f in (locale_dir / r).glob("**/*.md*")]
    articles = []
    for mdx_file in sorted(files):
        if tracked is not None and mdx_file.relative_to(root).as_posix() not in tracked:
            continue
        rel_path = mdx_file.relative_to(locale_dir).as_posix()
        fm = extract_frontmatter(mdx_file)
        
        leaf_name = mdx_file.stem
        title = fm.get("title", leaf_name.replace("_", " "))
        desc = fm.get("description", "")
        
        articles.append({
            "path": rel_path,
            "title": title,
            "description": desc,
            "locale": locale,
        })
    return articles

def _under_roots(path: str, roots) -> bool:
    return roots is not None and path.split("/", 1)[0] in roots


def _path_key(path: str):
    return PurePosixPath(path)


def _write_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_indexes(root: Path = ROOT_DIR, roots=None, tracked_only=False, log=print):
    """Rebuild every index (roots=None) or refresh only the entries under `roots`.

    tracked_only: index only files git tracks or has staged, so draft files still being
    written (untracked) never reach the indexes the sites read.
    """
    if roots is not None:
        roots = list(roots)
        for r in roots:
            if not r or "/" in r or "\\" in r or r in (".", ".."):
                raise ValueError(f"--roots takes top-level folder names, not paths: {r!r}")
        for name in ["_meta.json"] + [f"blog-{loc}-index-tree.json" for loc in LOCALES]:
            if not (root / name).exists():
                raise FileNotFoundError(f"{name} is missing; run a full rebuild first (no --roots)")
        previous_meta = _read_json(root / "_meta.json")["articles"]
    log("Scanning and rebuilding locale indexes..." if roots is None else f"Refreshing {', '.join(roots)}...")

    tracked = tracked_files(root) if tracked_only else None
    master_meta = {}
    for loc in LOCALES:
        scanned = scan_locale_tree(loc, root, roots, tracked)
        out_file = root / f"blog-{loc}-index-tree.json"
        if roots is None:
            articles = scanned
        else:
            kept = [a for a in _read_json(out_file)["articles"] if not _under_roots(a["path"], roots)]
            articles = sorted(kept + scanned, key=lambda a: _path_key(a["path"]))
        _write_json(out_file, {"locale": loc, "count": len(articles), "articles": articles})
        log(f"  • {out_file.name}: {len(articles)} articles indexed.")

        for art in scanned:
            p = art["path"]
            if p not in master_meta:
                master_meta[p] = {
                    "path": p,
                    "availableLocales": [loc],
                    "title": art["title"],
                }
            elif loc not in master_meta[p]["availableLocales"]:
                master_meta[p]["availableLocales"].append(loc)

    if roots is not None:
        kept = {p: e for p, e in previous_meta.items() if not _under_roots(p, roots)}
        merged = {**kept, **master_meta}
        order = sorted(merged, key=lambda p: (LOCALES.index(merged[p]["availableLocales"][0]), _path_key(p)))
        master_meta = {p: merged[p] for p in order}

    # Master multilingual meta
    master_meta_file = root / "_multilang_meta.json"
    _write_json(master_meta_file, master_meta)
    log(f"Master index updated -> {master_meta_file.name}")

    # Also update _meta.json with multilingual indices
    meta_file = root / "_meta.json"
    _write_json(meta_file, {"locales": LOCALES, "totalArticles": len(master_meta), "articles": master_meta})
    log(f"Master _meta.json updated -> {meta_file.name} ({len(master_meta)} articles)")

    log("Index generation complete!")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rebuild the locale indexes and _meta.json.")
    parser.add_argument("--roots", nargs="+", help="refresh only these top-level folders (e.g. 22_Home_Living)")
    parser.add_argument("--tracked-only", action="store_true", help="skip files git does not track (drafts)")
    args = parser.parse_args(argv)
    generate_indexes(roots=args.roots, tracked_only=args.tracked_only)


if __name__ == "__main__":
    main()

