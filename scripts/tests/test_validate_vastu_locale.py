import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import validate_vastu_locale as v  # noqa: E402


def make_fm(title="वास्तु शास्त्र में पूर्व दिशा का महत्व और घर पर असर", description=None,
            pub="2025-05-08", locale="hi", source="en", author="AstroFusion Editorial", kws=None,
            keys=None):
    if description is None:
        description = "द" * 120
    if kws is None:
        kws = ["एक", "दो", "तीन", "चार", "पांच"]
    lines = ["---"]
    values = {
        "title": f'"{title}"', "description": f'"{description}"', "pubDate": f"'{pub}'",
        "modifiedDate": "'2026-11-12'", "locale": f"'{locale}'", "sourceLocale": f"'{source}'",
        "author": f"'{author}'",
    }
    for k in keys or v.EXPECTED_KEYS:
        if k == "keywords":
            lines.append("keywords:")
            lines += [f'  - "{x}"' for x in kws]
        else:
            lines.append(f"{k}: {values[k]}")
    lines.append("---")
    return "\n".join(lines) + "\n"


EN = """---
title: X
---
# Intro

## What is it

<AIBlufSummary>
Summary words here that are removed entirely.
</AIBlufSummary>

One two three four five six seven eight nine ten.

<KundaliChart
  title="T"
  effects={["a > b"]}
  ctaHref="/kundali"
/>

## Keywords

dropped words dropped words

## Key Aspects

Eleven twelve thirteen fourteen fifteen.

## Classical Sanskrit Shastra Citation

<BookShlokaSnippet book="BPHS" />
more dropped text

## Previous Article

[x](y)
"""


class FrontmatterTests(unittest.TestCase):
    def run_rule(self, text, locale="hi", pub="2025-05-08"):
        fm = v.parse_frontmatter(text)
        return v.rule_frontmatter(fm, locale, pub)

    def test_valid(self):
        self.assertEqual(self.run_rule(make_fm()), [])

    def test_key_order(self):
        keys = list(v.EXPECTED_KEYS)
        keys[0], keys[1] = keys[1], keys[0]
        self.assertTrue(any("keys" in d for d in self.run_rule(make_fm(keys=keys))))

    def test_locale_mismatch(self):
        self.assertTrue(any("locale" in d for d in self.run_rule(make_fm(locale="ne"))))

    def test_source_locale(self):
        self.assertTrue(any("sourceLocale" in d for d in self.run_rule(make_fm(source="hi"))))

    def test_title_length_reports_length(self):
        out = self.run_rule(make_fm(title="छोटा"))
        self.assertTrue(any("title length 4" in d for d in out))

    def test_description_length(self):
        out = self.run_rule(make_fm(description="द" * 100))
        self.assertTrue(any("description length 100" in d for d in out))
        out = self.run_rule(make_fm(description="द" * 161))
        self.assertTrue(any("description length 161" in d for d in out))

    def test_keyword_count(self):
        self.assertTrue(any("keywords" in d for d in self.run_rule(make_fm(kws=["a"] * 4))))
        self.assertTrue(any("keywords" in d for d in self.run_rule(make_fm(kws=["a"] * 9))))
        self.assertEqual(self.run_rule(make_fm(kws=["a"] * 8)), [])

    def test_pubdate_mismatch(self):
        self.assertTrue(any("pubDate" in d for d in self.run_rule(make_fm(pub="2026-01-01"))))

    def test_pubdate_skipped_when_english_has_none(self):
        self.assertEqual(self.run_rule(make_fm(pub="2026-01-01"), pub=None), [])

    def test_underscore_in_title(self):
        out = self.run_rule(make_fm(title="वास्तु शास्त्र में पूर्व_दिशा का महत्व और घर पर असर"))
        self.assertTrue(any("underscore" in d for d in out))

    def test_missing_frontmatter(self):
        self.assertTrue(self.run_rule("# hi\n"))


class PlainMarkdownTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(v.rule_plain_markdown("# शीर्षक\n\nपाठ 1 < नहीं\n".replace("< ", "")), [])

    def test_forbidden_chars(self):
        for ch in "<>{}":
            self.assertTrue(v.rule_plain_markdown(f"पाठ {ch} पाठ"), ch)

    def test_ignores_fenced_code(self):
        self.assertEqual(v.rule_plain_markdown("```\na < b {x}\n```\nपाठ"), [])

    def test_jsx_name(self):
        out = v.rule_plain_markdown("<AIBlufSummary>\nपाठ\n</AIBlufSummary>")
        self.assertTrue(any("AIBlufSummary" in d for d in out))

    def test_links(self):
        self.assertTrue(v.rule_plain_markdown("देखें https://example.com"))
        self.assertTrue(v.rule_plain_markdown("देखें http://example.com"))


class EnglishInfoTests(unittest.TestCase):
    def test_retained(self):
        info = v.english_info(EN)
        # retained: intro heading line, "## What is it", sentence, "## Key Aspects", sentence
        # "# Intro"(2) "## What is it"(4) "One..ten."(10) "## Key Aspects"(3) "Eleven..."(5)
        self.assertEqual(info["retained_words"], 24)
        self.assertEqual(info["retained_h2"], 2)
        self.assertEqual(info["pubDate"], None)

    def test_pubdate(self):
        self.assertEqual(v.english_info("---\npubDate: '2025-05-08'\n---\n# A\n")["pubDate"], "2025-05-08")


class StructureTests(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(v.rule_structure("# A\n\n## B\n\n## C\n", 3), [])

    def test_two_h1(self):
        self.assertTrue(v.rule_structure("# A\n\n# B\n\n## C\n", 1))

    def test_no_h1(self):
        self.assertTrue(v.rule_structure("## C\n", 1))

    def test_too_few_h2(self):
        out = v.rule_structure("# A\n\n## B\n", 5)
        self.assertTrue(any("1" in d and "5" in d for d in out))

    def test_boundary_60_percent(self):
        self.assertEqual(v.rule_structure("# A\n" + "## B\n" * 3, 5), [])


class LengthTests(unittest.TestCase):
    def test_pass_and_fail_report_numbers(self):
        self.assertEqual(v.rule_length("शब्द " * 65, 100), [])
        out = v.rule_length("शब्द " * 64, 100)
        self.assertEqual(len(out), 1)
        self.assertIn("64", out[0])
        self.assertIn("100", out[0])
        self.assertIn("0.64", out[0])


class ScriptTests(unittest.TestCase):
    def test_devanagari(self):
        self.assertEqual(v.rule_script("वास्तु शास्त्र का महत्व"), [])

    def test_latin_heavy(self):
        self.assertTrue(v.rule_script("this is plain english text with एक शब्द"))

    def test_latin_in_brackets_ignored(self):
        self.assertEqual(v.rule_script("भार वहन क्षमता (bearing capacity) महत्वपूर्ण है"), [])

    def test_latin_outside_brackets_counts(self):
        self.assertTrue(v.rule_script("भार bearing capacity foundation depth"))


class LanguageTests(unittest.TestCase):
    NE = "यो घर राम्रो छ। यो हुन्छ। गर्नुहोस् । तपाईं पनि। भने ठीक छ।"
    HI = "यह घर अच्छा है। ये हैं। करें। आपका घर। आपके घर। है।"

    def test_ne_ok(self):
        self.assertEqual(v.rule_language(self.NE, "ne"), [])

    def test_hi_ok(self):
        self.assertEqual(v.rule_language(self.HI, "hi"), [])

    def test_hindi_text_in_ne_fails(self):
        self.assertTrue(v.rule_language(self.HI, "ne"))

    def test_nepali_text_in_hi_fails(self):
        self.assertTrue(v.rule_language(self.NE, "hi"))

    def test_whole_words_only(self):
        # तपाईंको must not count as तपाईं
        self.assertTrue(v.rule_language("तपाईंको " * 6, "ne"))

    def test_ne_too_many_hindi_markers(self):
        self.assertTrue(v.rule_language(self.NE + " है हैं करें आपका आपके", "ne"))


class TemplateTests(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(v.rule_template("वास्तु लेख"), [])

    def test_each_phrase(self):
        for p in v.TEMPLATE_PHRASES:
            self.assertTrue(v.rule_template(f"पाठ {p} पाठ"), p)


class DuplicateTests(unittest.TestCase):
    def para(self, n):
        return f"अनुच्छेद संख्या {n} " + "शब्द " * 30

    def test_flags_shared(self):
        a = "\n\n".join(self.para(i) for i in range(10))
        b = "\n\n".join(self.para(i) for i in range(4)) + "\n\n" + "\n\n".join(self.para(100 + i) for i in range(6))
        out = v.rule_duplicate({"a.mdx": a, "b.mdx": b})
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0][0], "a.mdx")
        self.assertEqual(out[0][1], "b.mdx")

    def test_not_flagged_at_30_percent(self):
        a = "\n\n".join(self.para(i) for i in range(10))
        b = "\n\n".join(self.para(i) for i in range(3)) + "\n\n" + "\n\n".join(self.para(100 + i) for i in range(7))
        self.assertEqual(v.rule_duplicate({"a.mdx": a, "b.mdx": b}), [])

    def test_short_paragraphs_ignored(self):
        a = "\n\n".join(f"छोटा {i}" for i in range(10))
        self.assertEqual(v.rule_duplicate({"a.mdx": a, "b.mdx": a}), [])

    def test_whitespace_normalised(self):
        p = self.para(1)
        self.assertEqual(len(v.rule_duplicate({"a.mdx": p, "b.mdx": p.replace(" ", "  ") })), 1)


class FileLevelTests(unittest.TestCase):
    def test_find_files_skips_meta_and_directions_docs(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for rel in ["hi/18_Vastu/A/x.mdx", "hi/18_Vastu/A/_meta.json",
                        "hi/18_Vastu/Directions_Docs/y.mdx", "ne/18_Vastu/B/z.mdx"]:
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("x")
            names = sorted(str(p.relative_to(root)) for p in v.find_files(root, None, None))
            self.assertEqual(names, ["hi/18_Vastu/A/x.mdx", "ne/18_Vastu/B/z.mdx"])
            names = sorted(str(p.relative_to(root)) for p in v.find_files(root, "ne", "B"))
            self.assertEqual(names, ["ne/18_Vastu/B/z.mdx"])


if __name__ == "__main__":
    unittest.main()
