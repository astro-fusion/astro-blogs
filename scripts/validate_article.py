#!/usr/bin/env python3
"""Validate articles that have no source text to compare against.

Covers:
  en/22_Home_Living, en/23_Interior_Design    docs/living-articles-spec.md
  en/18_Vastu                                 plain-Markdown rewrite (pubDate optional, at least 400 words)
  hi|ne/22_Home_Living, hi|ne/23_Interior_Design
                                              same structure as English plus the script and language rules of
                                              scripts/validate_vastu_locale.py, checked against the English file
Hindi and Nepali Vastu files are checked by scripts/validate_vastu_locale.py.

Usage:
    python3 scripts/validate_article.py [--locale en|hi|ne] [--topic 18_Vastu|22_Home_Living|23_Interior_Design]
                                        [--section <folder>] [files...] [--summary]

Silent with exit code 0 when every file passes. Otherwise prints one line per problem,
"<path>: <rule>: <message>" ("<path>: <rule>: warning: <message>" for a warning), and exits 1 if any
file has an error. Warnings alone do not fail. Python 3 standard library only.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_vastu_locale as v  # noqa: E402

ROOT = v.ROOT
LOCALES = ("en", "hi", "ne")
VASTU = "18_Vastu"
LIVING_TOPICS = ("22_Home_Living", "23_Interior_Design")
TOPICS = (VASTU,) + LIVING_TOPICS
EN_KEYS = ["title", "description", "pubDate", "modifiedDate", "locale", "author", "keywords"]
FILE_NAME = re.compile(r"^\d{6}_[a-z0-9_]+\.mdx$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RULES = ["path", "frontmatter", "plain-markdown", "structure", "length", "measurement", "claims",
         "source", "script", "language", "template"]

LIVING_MIN_H2 = 5
FAQ_MIN, FAQ_MAX = 4, 6
LIVING_WORDS = (900, 1500)          # target; outside it is a warning
LIVING_HARD_WORDS = (800, 1800)     # outside it is an error
VASTU_MIN_WORDS = 400               # Hindi/Nepali ratio (65%) comes from validate_vastu_locale.rule_length

DEVA = "ऀ-ॿ"
FAQ_HEADING = re.compile(r"\bFAQs?\b|frequently asked|common questions|प्रश्न|सवाल", re.I)

# ---------------------------------------------------------------- measurement

_METRIC = (r"\d+(?:[.,]\d+)?(?:\s*(?:x|×|by)\s*\d+(?:[.,]\d+)?)*\s*"
           r"(?:mm|cm|m²|m2|sq\.?\s?m|m|सेंटीमीटर|सेन्टिमिटर|सेमी|मिमी|मीटर|मिटर|मी)"
           rf"(?![A-Za-z{DEVA}])")
_IMPERIAL = (r"\s*\([^()]*?\d[^()]*?(?:ft|feet|foot|inches|inch|in|फुट|फीट|फिट|इंच|इन्च)"
             rf"(?![A-Za-z{DEVA}])[^()]*\)")
MEASUREMENT = re.compile(_METRIC + _IMPERIAL)


def has_metric_with_imperial(text):
    """True if text has a metric measurement followed by a bracketed imperial equivalent."""
    return MEASUREMENT.search(text) is not None


# ---------------------------------------------------------------- banned claims

PERCENT = re.compile(r"\d+(?:\.\d+)?\s?(?:%|percent\b|per cent\b)", re.I)
CLAIM_WORD = re.compile(r"\b(?:increas\w*|improv\w*|rise[sn]?|rising|rose|boost\w*|reduc\w*|growth|"
                        r"more\s+customers)\b", re.I)
CLAIM_WINDOW = 60
RESEARCH = [
    re.compile(r"\bstudies\s+(?:have\s+)?show(?:s|n|ed)?\b", re.I),
    re.compile(r"\bresearch\s+(?:has\s+)?(?:shows?|shown|suggests?|suggested|confirms?|confirmed)\b", re.I),
    re.compile(r"\bscientifically\s+proven\b", re.I),
    re.compile(r"\bscience\s+(?:has\s+)?(?:proves?|proven|validates?|validated)\b", re.I),
]
_NUMBER_WORDS = ("a few|a couple of|few|several|one|two|three|four|five|six|seven|eight|nine|ten|"
                 "eleven|twelve")
WITHIN = re.compile(rf"\bwithin\s+(?:\d+|{_NUMBER_WORDS})\s+(?:weeks?|months?)\b", re.I)
GUARANTEE = re.compile(r"\bguarantee(?:s|d|ing)?\b", re.I)
# A negator up to five words before "guarantee" in the same clause (no punctuation in between):
# "no guarantee", "not guaranteed", "cannot be guaranteed", "not a proven result or a guarantee".
GUARANTEE_NEGATION = re.compile(r"\b(?:no|not|never|cannot|can't)(?:\s+[^\s.,;:!?]+){0,5}?\s+$", re.I)
ASHTAKAVARGA = re.compile(r"\bash?ta?ka?\s?varga\w*|अष्टकवर्ग", re.I)
CURRENCY = [
    re.compile(r"(?:\bRs\.?|\bNPR|\bINR|₹|\$|" rf"(?<![{DEVA}])(?:रु|रू)\.?)\s?\d[\d,]*(?:\.\d+)?"),
    re.compile(r"\d[\d,]*(?:\.\d+)?\s?(?:Rs|NPR|INR|रुपये|रुपए|रुपया|रुपैयाँ)" rf"(?![A-Za-z{DEVA}])"),
]


def _percent_claims(text):
    out = []
    for block in re.split(r"\n\s*\n", text):
        for pm in PERCENT.finditer(block):
            best = None
            for wm in CLAIM_WORD.finditer(block):
                gap = pm.start() - wm.end() if wm.end() <= pm.start() else wm.start() - pm.end()
                if 0 <= gap <= CLAIM_WINDOW and (best is None or gap < best[0]):
                    best = (gap, wm)
            if best:
                wm = best[1]
                snippet = block[min(pm.start(), wm.start()):max(pm.end(), wm.end())]
                out.append(f"percentage claim {' '.join(snippet.split())!r}")
    return out


def _ashtakavarga_allowed(rel):
    return len(rel.parts) > 2 and rel.parts[1] == VASTU and rel.parts[2].startswith("1808")


def rule_claims(text, rel):
    """Banned claim patterns. rel is the path relative to the repo root (locale/topic/section/file)."""
    out = _percent_claims(text)
    for rx in RESEARCH:
        out += [f"unsupported research claim {m.group(0)!r}" for m in rx.finditer(text)]
    out += [f"time-bound promise {m.group(0)!r}" for m in WITHIN.finditer(text)]
    for m in GUARANTEE.finditer(text):
        if not GUARANTEE_NEGATION.search(text[max(0, m.start() - 60):m.start()]):
            out.append(f"guarantee used as a promise {m.group(0)!r}")
    if not _ashtakavarga_allowed(rel):
        out += [f"Ashtakavarga outside 18_Vastu/1808 {m.group(0)!r}" for m in ASHTAKAVARGA.finditer(text)]
    if len(rel.parts) > 1 and rel.parts[1] in LIVING_TOPICS:
        spans = []
        for rx in CURRENCY:
            for m in rx.finditer(text):
                if not any(m.start() < e and s < m.end() for s, e in spans):
                    spans.append((m.start(), m.end()))
        out += [f"currency amount {text[s:e]!r}" for s, e in sorted(spans)]
    return out


# ---------------------------------------------------------------- other rules

def rule_path(rel):
    name = rel.name
    return [] if FILE_NAME.match(name) else [f"file name {name!r} does not match {FILE_NAME.pattern}"]


def _rule_dates(fm):
    return [f"{k} {fm['values'][k]!r} is not a YYYY-MM-DD date"
            for k in ("pubDate", "modifiedDate") if k in fm["values"] and not DATE.match(fm["values"][k])]


def rule_frontmatter_en(fm, require_pubdate=True):
    if not fm["found"]:
        return ["missing or unterminated frontmatter"]
    errs = []
    expected = EN_KEYS if require_pubdate or "pubDate" in fm["keys"] else [k for k in EN_KEYS if k != "pubDate"]
    if fm["keys"] != expected:
        errs.append(f"keys {fm['keys']} are not exactly {expected} in that order")
    vals = fm["values"]
    if vals.get("locale") != "en":
        errs.append(f"locale {vals.get('locale')!r} must be 'en'")
    if not vals.get("author", "").strip():
        errs.append("author is empty")
    errs += _rule_dates(fm)
    errs += v.rule_common_fields(fm)
    return errs


def rule_structure(text, title, min_h2):
    body = v.body_of(text)
    h1s, h2s, faq_h3, in_faq = [], 0, None, False
    for line in v.iter_lines_outside_fences(body):
        if line.startswith("# "):
            h1s.append(line[2:].strip())
            in_faq = False
        elif line.startswith("## "):
            h2s += 1
            in_faq = bool(FAQ_HEADING.search(line[3:]))
            if in_faq:
                faq_h3 = 0          # the last FAQ-like '## ' heading is the FAQ section
        elif line.startswith("### ") and in_faq:
            faq_h3 += 1
    errs = []
    if len(h1s) != 1:
        errs.append(f"{len(h1s)} '# ' headings, expected exactly 1")
    elif h1s[0] != title.strip():
        errs.append(f"'# ' heading {h1s[0]!r} does not equal the title {title.strip()!r}")
    if h2s < min_h2:
        errs.append(f"{h2s} '## ' headings, need at least {min_h2}")
    if faq_h3 is None:
        errs.append("no FAQ section (a '## ' heading such as 'FAQ')")
    elif not FAQ_MIN <= faq_h3 <= FAQ_MAX:
        errs.append(f"FAQ section has {faq_h3} '### ' questions, need {FAQ_MIN}-{FAQ_MAX}")
    if not text.endswith("\n") or text.endswith("\n\n"):
        errs.append("file must end with exactly one newline")
    return errs


def word_count(text):
    """Whitespace-separated tokens that contain at least one letter or digit."""
    return sum(1 for t in text.split() if any(c.isalnum() for c in t))


def rule_length_living(words):
    lo, hi = LIVING_WORDS
    hard_lo, hard_hi = LIVING_HARD_WORDS
    if words < hard_lo or words > hard_hi:
        return [(f"{words} words, need {lo}-{hi} (error below {hard_lo} or above {hard_hi})", False)]
    if words < lo or words > hi:
        return [(f"{words} words, aim for {lo}-{hi}", True)]
    return []


def rule_digits(body):
    n = len(re.findall(r"[०-९]", body))
    return [f"{n} Devanagari digit(s); use Latin digits"] if n else []


# ---------------------------------------------------------------- driver

def validate_text(text, rel, english_text=None):
    """Return [(rule, message, is_warning)] for one article. rel: path relative to the repo root."""
    rel = Path(rel)
    parts = rel.parts
    locale = parts[0] if parts else ""
    topic = parts[1] if len(parts) > 1 else ""
    if locale not in LOCALES or topic not in TOPICS or (locale != "en" and topic == VASTU):
        hint = " (use scripts/validate_vastu_locale.py)" if topic == VASTU else ""
        return [("path", f"{rel} is not a locale/topic this checker covers{hint}", False)]

    problems = []

    def add(rule, msgs, warning=False):
        problems.extend((rule, m, warning) for m in msgs)

    fm = v.parse_frontmatter(text)
    title = fm["values"].get("title", "")
    body = v.body_of(text)
    living = topic in LIVING_TOPICS
    words = word_count(body)

    if living:
        add("path", rule_path(rel))
    if locale == "en":
        add("frontmatter", rule_frontmatter_en(fm, require_pubdate=living))
    else:
        en_rel = Path("en", *parts[1:])
        en_pub, en_words = None, 0
        if english_text is None:
            add("source", [f"English file {en_rel} not found"])
        else:
            en_fm = v.parse_frontmatter(english_text)
            en_pub = en_fm["values"].get("pubDate") or None
            en_words = word_count(v.body_of(english_text))
        add("frontmatter", v.rule_frontmatter(fm, locale, en_pub) + _rule_dates(fm))
    add("plain-markdown", v.rule_plain_markdown(body))
    add("structure", rule_structure(text, title, LIVING_MIN_H2 if living else 0))
    if locale == "en" and living:
        for msg, warning in rule_length_living(words):
            add("length", [msg], warning)
    elif locale == "en":
        if words < VASTU_MIN_WORDS:
            add("length", [f"{words} words, need at least {VASTU_MIN_WORDS}"])
    elif english_text is not None:
        add("length", v.rule_length(" ".join(["w"] * words), en_words))
    if living and not has_metric_with_imperial(body):
        add("measurement", ["no metric measurement with a bracketed imperial equivalent, e.g. '75 cm (2 ft 6 in)'"])
    add("claims", rule_claims(text, rel))
    if locale != "en":
        add("script", v.rule_script(body) + rule_digits(body))
        add("language", v.rule_language(body, locale))
        add("template", v.rule_template(body))
    return problems


def validate_file(path, root):
    rel = path.resolve().relative_to(root)
    text = path.read_text(encoding="utf-8")
    english = None
    if rel.parts and rel.parts[0] != "en":
        en_path = root / Path("en", *rel.parts[1:])
        if en_path.is_file():
            english = en_path.read_text(encoding="utf-8")
    return validate_text(text, rel, english)


def find_files(root, locale=None, topic=None, section=None):
    files = []
    for loc in ([locale] if locale else LOCALES):
        for top in ([topic] if topic else TOPICS):
            if loc != "en" and top == VASTU:
                continue
            base = root / loc / top
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


def main(argv=None, root=ROOT):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--locale", choices=LOCALES)
    ap.add_argument("--topic", choices=TOPICS)
    ap.add_argument("--section", help="section folder name, e.g. 2201_Room_by_Room")
    ap.add_argument("--summary", action="store_true", help="print counts per rule and passing files")
    ap.add_argument("files", nargs="*")
    args = ap.parse_args(argv)
    if args.locale in ("hi", "ne") and args.topic == VASTU:
        ap.error("Hindi and Nepali Vastu articles are checked by scripts/validate_vastu_locale.py")

    root = Path(root).resolve()
    files = [Path(f).resolve() for f in args.files] if args.files else find_files(
        root, args.locale, args.topic, args.section)

    def label(p):
        try:
            return str(p.resolve().relative_to(root))
        except ValueError:
            return str(p)

    errors, warnings = Counter(), 0
    failing = 0
    for f in files:
        try:
            problems = validate_file(f, root)
        except ValueError:
            problems = [("path", f"{f} is not inside {root}", False)]
        except OSError as e:
            problems = [("path", f"cannot read: {e}", False)]
        for rule, msg, warning in problems:
            print(f"{label(f)}: {rule}: " + ("warning: " if warning else "") + msg)
            if warning:
                warnings += 1
            else:
                errors[rule] += 1
        if any(not w for _, _, w in problems):
            failing += 1
    if args.summary:
        print("--- summary ---")
        for rule in RULES:
            print(f"{rule}: {errors[rule]}")
        print(f"warnings: {warnings}")
        print(f"files checked: {len(files)}; passing: {len(files) - failing}; failing: {failing}")
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
