#!/usr/bin/env python3
"""Validate Hindi and Nepali Vastu articles against docs/vastu-locale-articles-spec.md.

Usage:
    python3 scripts/validate_vastu_locale.py [--locale hi|ne] [--section <folder>] [files...] [--summary]

Prints one line per problem: "<path>: <rule>: <detail>". Exit code 1 if any file has an error.
Python 3 standard library only.
"""
import argparse
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("hi", "ne")
EXPECTED_KEYS = ["title", "description", "pubDate", "modifiedDate", "locale", "sourceLocale", "author", "keywords"]
DROPPED_PREFIXES = ("Keywords", "Resources", "Classical Sanskrit Shastra Citation", "Previous Article", "Next Article")
JSX_NAMES = ("AIBlufSummary", "KundaliChart", "BookShlokaSnippet", "YogaDeepLink")
TEMPLATE_PHRASES = ("Executive Summary", "Classical Shastra References", "Illustrative Chart",
                    "कुण्डली विश्लेषण", "Check Your Kundali Analysis")
NE_MARKERS = ("छ", "हुन्छ", "गर्नुहोस्", "तपाईं", "भने", "पनि")
HI_MARKERS = ("है", "हैं", "करें", "आपका", "आपके")
HI_FILE_NE_MARKERS = ("हुन्छ", "गर्नुहोस्", "तपाईं")
RULES = ["source", "frontmatter", "plain-markdown", "structure", "length", "script", "language", "template", "duplicate"]


# ---------------------------------------------------------------- parsing

def split_frontmatter(text):
    """Return (frontmatter_text or None, body)."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fm = text[4:end]
    rest = text[end + 4:]
    nl = rest.find("\n")
    rest = rest[nl + 1:] if nl != -1 else ""
    return fm, rest


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_frontmatter(text):
    """Return dict: found, keys (ordered), values (scalar dict), keywords (list), inline_keywords."""
    fm_text, _ = split_frontmatter(text)
    result = {"found": fm_text is not None, "keys": [], "values": {}, "keywords": [], "inline_keywords": False}
    if fm_text is None:
        return result
    current = None
    for line in fm_text.split("\n"):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if m:
            current = m.group(1)
            result["keys"].append(current)
            val = m.group(2)
            result["values"][current] = _unquote(val)
            if current == "keywords" and val.strip():
                result["inline_keywords"] = True
        elif current == "keywords":
            li = re.match(r"^\s*-\s+(.*)$", line)
            if li:
                result["keywords"].append(_unquote(li.group(1)))
    return result


def body_of(text):
    return split_frontmatter(text)[1]


def iter_lines_outside_fences(text):
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line


_OPEN_TAG = re.compile(r"<([A-Z][A-Za-z0-9]*)\b")


def strip_jsx_blocks(text):
    """Remove JSX blocks (<Name ...> ... </Name> or self-closing, multi-line)."""
    out = []
    i, n = 0, len(text)
    while i < n:
        m = _OPEN_TAG.match(text, i) if text[i] == "<" else None
        if not m:
            out.append(text[i])
            i += 1
            continue
        name = m.group(1)
        j = m.end()
        quote, depth = None, 0
        while j < n:
            c = text[j]
            if quote:
                if c == quote:
                    quote = None
            elif c in "\"'":
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            elif c == ">" and depth <= 0:
                break
            j += 1
        if j >= n:
            out.append(text[i])
            i += 1
            continue
        if text[j - 1] == "/":
            i = j + 1
            continue
        close = text.find(f"</{name}>", j)
        i = (close + len(name) + 3) if close != -1 else j + 1
    return "".join(out)


def english_info(text):
    """pubDate, retained word count and retained '## ' count of an English article."""
    fm = parse_frontmatter(text)
    body = body_of(text)
    kept, dropping, in_fence = [], False, False
    h2 = 0
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            dropping = line[3:].strip().startswith(DROPPED_PREFIXES)
            if not dropping:
                h2 += 1
        if not dropping:
            kept.append(line)
    stripped = strip_jsx_blocks("\n".join(kept))
    pub = fm["values"].get("pubDate") if fm["found"] else None
    return {"pubDate": pub or None, "retained_words": len(stripped.split()), "retained_h2": h2}


# ---------------------------------------------------------------- rules

def rule_common_fields(fm):
    """Title, description and keyword checks shared by every article spec."""
    errs = []
    vals = fm["values"]
    title = vals.get("title", "")
    if not 30 <= len(title) <= 65:
        errs.append(f"title length {len(title)} not in 30-65")
    if "_" in title:
        errs.append("title contains an underscore")
    desc = vals.get("description", "")
    if not 110 <= len(desc) <= 160:
        errs.append(f"description length {len(desc)} not in 110-160")
    if fm["inline_keywords"]:
        errs.append("keywords must be a YAML list")
    elif not 5 <= len(fm["keywords"]) <= 8:
        errs.append(f"keywords count {len(fm['keywords'])} not in 5-8")
    return errs


def rule_frontmatter(fm, locale, en_pubdate):
    errs = []
    if not fm["found"]:
        return ["missing or unterminated frontmatter"]
    if fm["keys"] != EXPECTED_KEYS:
        errs.append(f"keys {fm['keys']} are not exactly {EXPECTED_KEYS} in that order")
    vals = fm["values"]
    if vals.get("locale") != locale:
        errs.append(f"locale {vals.get('locale')!r} does not match folder {locale!r}")
    if vals.get("sourceLocale") != "en":
        errs.append(f"sourceLocale {vals.get('sourceLocale')!r} must be 'en'")
    errs += rule_common_fields(fm)
    if en_pubdate is not None and vals.get("pubDate") != en_pubdate:
        errs.append(f"pubDate {vals.get('pubDate')!r} differs from English {en_pubdate!r}")
    return errs


def rule_plain_markdown(body):
    errs = []
    counts = Counter()
    jsx, urls = set(), False
    for line in iter_lines_outside_fences(body):
        for ch in "<>{}":
            counts[ch] += line.count(ch)
        jsx.update(re.findall(r"</?([A-Z][A-Za-z0-9]*)", line))
        jsx.update(n for n in JSX_NAMES if n in line)
        if re.search(r"https?://", line):
            urls = True
    for ch in "<>{}":
        if counts[ch]:
            errs.append(f"{counts[ch]} occurrence(s) of {ch!r}")
    if jsx:
        errs.append("JSX component names: " + ", ".join(sorted(jsx)))
    if urls:
        errs.append("contains http:// or https:// link")
    return errs


def rule_structure(body, en_retained_h2):
    h1 = h2 = 0
    for line in iter_lines_outside_fences(body):
        if line.startswith("# "):
            h1 += 1
        elif line.startswith("## "):
            h2 += 1
    errs = []
    if h1 != 1:
        errs.append(f"{h1} '# ' headings, expected exactly 1")
    if h2 * 10 < 6 * en_retained_h2:
        errs.append(f"{h2} '## ' headings, need at least 60% of English retained {en_retained_h2}")
    return errs


def rule_length(body, en_retained_words):
    words = len(body.split())
    ratio = words / en_retained_words if en_retained_words else 1.0
    if words * 100 >= 65 * en_retained_words:
        return []
    return [f"{words} words vs English retained {en_retained_words}, ratio {ratio:.2f}, need 0.65"]


def _is_deva_letter(c):
    return "ऀ" <= c <= "ॿ" and unicodedata.category(c)[0] in "LM"


def rule_script(body):
    text = re.sub(r"\([^)]*[A-Za-z][^)]*\)", " ", body)
    deva = sum(1 for c in text if _is_deva_letter(c))
    other = sum(1 for c in text if not ("ऀ" <= c <= "ॿ") and c.isalpha())
    total = deva + other
    ratio = deva / total if total else 0.0
    if ratio >= 0.8:
        return []
    return [f"Devanagari is {ratio:.0%} of {total} letters, need 80%"]


def _count_markers(body, markers):
    tokens = re.findall(r"[ऀ-ॣ०-ॿ]+", body)
    return sum(1 for t in tokens if t in markers)


def rule_language(body, locale):
    ne = _count_markers(body, NE_MARKERS if locale == "ne" else HI_FILE_NE_MARKERS)
    hi = _count_markers(body, HI_MARKERS)
    errs = []
    if locale == "ne":
        if ne < 5:
            errs.append(f"{ne} Nepali markers, need at least 5")
        if hi >= 5:
            errs.append(f"{hi} Hindi markers, need fewer than 5")
    else:
        if hi < 5:
            errs.append(f"{hi} Hindi markers, need at least 5")
        if ne >= 3:
            errs.append(f"{ne} Nepali markers, need fewer than 3")
    return errs


def rule_template(body):
    return [f"old template phrase {p!r}" for p in TEMPLATE_PHRASES if p in body]


def paragraphs(text):
    out = set()
    for block in re.split(r"\n\s*\n", text):
        norm = " ".join(block.split())
        if len(norm) > 80:
            out.add(norm)
    return out


def rule_duplicate(bodies):
    """bodies: {path: body}. Returns [(path_a, path_b, detail)] for pairs sharing more than 30%."""
    paras = {p: paragraphs(b) for p, b in bodies.items()}
    index = defaultdict(list)
    for p, s in paras.items():
        for para in s:
            index[para].append(p)
    shared = Counter()
    for owners in index.values():
        for i in range(len(owners)):
            for j in range(i + 1, len(owners)):
                shared[(owners[i], owners[j])] += 1
    order = {p: i for i, p in enumerate(bodies)}
    out = []
    for (a, b), n in shared.items():
        smaller = min(len(paras[a]), len(paras[b]))
        if smaller and n / smaller > 0.3:
            a, b = sorted((a, b), key=order.get)
            out.append((a, b, f"shares {n} of {smaller} paragraphs ({n * 100 // smaller}%) with {b}"))
    return sorted(out, key=lambda t: (order[t[0]], order[t[1]]))


# ---------------------------------------------------------------- driver

def find_files(root, locale, section):
    files = []
    for loc in ([locale] if locale else LOCALES):
        base = root / loc / "18_Vastu"
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.mdx")):
            rel = p.relative_to(base)
            if "Directions_Docs" in rel.parts:
                continue
            if section and (len(rel.parts) < 2 or rel.parts[0] != section):
                continue
            files.append(p)
    return files


def validate_file(path, root):
    """Return list of (rule, detail) for one file."""
    problems = []
    rel = path.resolve().relative_to(root)
    locale = rel.parts[0]
    text = path.read_text(encoding="utf-8")
    en_rel = Path("en", *rel.parts[1:])
    en_path = root / en_rel
    if not en_path.is_file():
        problems.append(("source", f"English file {en_rel} not found"))
        en = {"pubDate": None, "retained_words": 0, "retained_h2": 0}
    else:
        en = english_info(en_path.read_text(encoding="utf-8"))
    body = body_of(text)
    checks = [
        ("frontmatter", rule_frontmatter(parse_frontmatter(text), locale, en["pubDate"])),
        ("plain-markdown", rule_plain_markdown(body)),
        ("structure", rule_structure(body, en["retained_h2"])),
        ("length", rule_length(body, en["retained_words"])),
        ("script", rule_script(body)),
        ("language", rule_language(body, locale)),
        ("template", rule_template(body)),
    ]
    for rule, details in checks:
        problems += [(rule, d) for d in details]
    return problems


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--locale", choices=LOCALES)
    ap.add_argument("--section", help="section folder name, e.g. 1803_Directions")
    ap.add_argument("--summary", action="store_true", help="print counts per rule and passing files")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args(argv)

    if args.files:
        files = [Path(f).resolve() for f in args.files]
    else:
        files = find_files(root, args.locale, args.section)

    def label(p):
        try:
            return str(p.resolve().relative_to(root))
        except ValueError:
            return str(p)

    results = {}
    for f in files:
        try:
            results[f] = validate_file(f, root)
        except (ValueError, OSError) as e:
            results[f] = [("source", f"cannot validate: {e}")]

    if len(files) > 1:
        by_locale = defaultdict(dict)
        for f in files:
            try:
                loc = f.resolve().relative_to(root).parts[0]
                by_locale[loc][f] = body_of(f.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                continue
        for bodies in by_locale.values():
            per_file = defaultdict(list)
            for a, b, detail in rule_duplicate(bodies):
                pct = int(re.search(r"\((\d+)%\)", detail).group(1))
                per_file[a].append((pct, detail.split(" with ")[0], b))
                per_file[b].append((pct, detail.split(" with ")[0], a))
            for f, hits in per_file.items():
                pct, what, other = max(hits, key=lambda h: h[0])
                results[f].append(("duplicate", f"more than 30% of paragraphs shared with {len(hits)} file(s); "
                                   f"highest: {what} with {label(other)}"))

    counts = Counter()
    for f in files:
        for rule, detail in results[f]:
            print(f"{label(f)}: {rule}: {detail}")
            counts[rule] += 1
    failing = sum(1 for f in files if results[f])
    if args.summary:
        print("--- summary ---")
        for rule in RULES:
            print(f"{rule}: {counts[rule]}")
        print(f"files checked: {len(files)}; passing: {len(files) - failing}; failing: {failing}")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
