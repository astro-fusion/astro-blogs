import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import validate_article as a  # noqa: E402

LIVING = "en/22_Home_Living/2201_Room_by_Room/220101_setting_up_a_small_bedroom.mdx"
INTERIOR = "en/23_Interior_Design/2301_Layout_and_Furniture/230101_clearances.mdx"
VASTU = "en/18_Vastu/1803_Directions/180301_East_Direction.mdx"
ASTRO_VASTU = "en/18_Vastu/1808_Astro-Vastu_Astrology_with_Vastu/180801_Planets.mdx"
HI_LIVING = "hi/22_Home_Living/2201_Room_by_Room/220101_setting_up_a_small_bedroom.mdx"
NE_LIVING = "ne/22_Home_Living/2201_Room_by_Room/220101_setting_up_a_small_bedroom.mdx"

EN_TITLE = "Setting up a small bedroom with bed and wardrobe"
HI_TITLE = "छोटे शयनकक्ष में बिस्तर और अलमारी कैसे रखें"


def count_words(text):
    return sum(1 for t in text.split() if any(c.isalnum() for c in t))


def frontmatter(title=EN_TITLE, description="A" * 120, pub="2026-11-13", modified="2026-11-13",
                locale="en", source=None, author="AstroFusion Editorial", kws=None, keys=None):
    if kws is None:
        kws = ["one", "two", "three", "four", "five"]
    values = {"title": f'"{title}"', "description": f'"{description}"', "pubDate": f"'{pub}'",
              "modifiedDate": f"'{modified}'", "locale": f"'{locale}'", "sourceLocale": f"'{source}'",
              "author": f"'{author}'"}
    if keys is None:
        keys = ["title", "description", "pubDate", "modifiedDate", "locale"]
        keys += ["sourceLocale"] if source else []
        keys += ["author", "keywords"]
    lines = ["---"]
    for k in keys:
        if k == "keywords":
            lines.append("keywords:")
            lines += [f'  - "{x}"' for x in kws]
        else:
            lines.append(f"{k}: {values[k]}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def en_body(title=EN_TITLE, words=1000, h2=5, faq=4, measurement=True, extra="", faq_heading="FAQ"):
    parts = [f"# {title}", "", "After reading this you can plan the room."]
    if measurement:
        parts += ["", "Leave 75 cm (2 ft 6 in) beside the bed."]
    if extra:
        parts += ["", extra]
    for i in range(h2 - 1):
        parts += ["", f"## Section number {i}", "", "Plain words about the room."]
    if faq_heading:
        parts += ["", f"## {faq_heading}"]
    for i in range(faq):
        parts += ["", f"### Question number {i}?", "", "Answer from the article."]
    have = count_words("\n".join(parts))
    if words > have:
        parts.insert(3, "room " * (words - have))
    return "\n".join(parts).rstrip() + "\n"


def en_article(**kw):
    fm_kw = {k: kw.pop(k) for k in list(kw) if k in ("description", "pub", "modified", "locale", "author",
                                                     "kws", "keys", "source")}
    title = kw.get("title", EN_TITLE)
    return frontmatter(title=title, **fm_kw) + "\n" + en_body(**kw)


def hi_body(words=700, title=HI_TITLE, extra=""):
    parts = [f"# {title}", "", "यह लेख आपके कमरे के लिए है। आप इसे पढ़कर योजना करें।",
             "", "बिस्तर के पास 75 सेमी (2 फुट 6 इंच) जगह छोड़ें। आपका कमरा खुला रहेगा।"]
    if extra:
        parts += ["", extra]
    for i in range(4):
        parts += ["", f"## कमरे का भाग {i + 1}", "", "यह भाग कमरे के बारे में है। ध्यान दें।"]
    parts += ["", "## अक्सर पूछे जाने वाले प्रश्न"]
    for i in range(4):
        parts += ["", f"### क्या यह प्रश्न {i + 1} है?", "", "हाँ, यह उत्तर है।"]
    have = count_words("\n".join(parts))
    if words > have:
        parts.insert(3, "कमरा " * (words - have))
    return "\n".join(parts).rstrip() + "\n"


def hi_article(words=700, locale="hi", source="en", title=HI_TITLE, extra="", **fm_kw):
    return (frontmatter(title=title, description="द" * 120, locale=locale, source=source,
                        kws=["एक", "दो", "तीन", "चार", "पांच"], **fm_kw)
            + "\n" + hi_body(words=words, title=title, extra=extra))


def rules(problems, warnings=False):
    return [p[0] for p in problems if p[2] == warnings]


def messages(problems, rule):
    return [p[1] for p in problems if p[0] == rule]


class PathRuleTests(unittest.TestCase):
    def test_valid_name(self):
        self.assertEqual(a.rule_path(Path(LIVING)), [])

    def test_bad_names(self):
        for name in ("220101_Setting_Up.mdx", "22010_setting.mdx", "220101_setting.md", "220101-setting.mdx",
                     "220101_.mdx"):
            p = Path("en/22_Home_Living/2201_Room_by_Room") / name
            self.assertTrue(a.rule_path(p), name)


class FrontmatterTests(unittest.TestCase):
    def run_rule(self, text, require_pubdate=True):
        return a.rule_frontmatter_en(a.v.parse_frontmatter(text), require_pubdate)

    def test_valid(self):
        self.assertEqual(self.run_rule(frontmatter()), [])

    def test_key_order(self):
        keys = ["description", "title", "pubDate", "modifiedDate", "locale", "author", "keywords"]
        self.assertTrue(any("keys" in d for d in self.run_rule(frontmatter(keys=keys))))

    def test_source_locale_not_allowed_in_english(self):
        self.assertTrue(any("keys" in d for d in self.run_rule(frontmatter(source="en"))))

    def test_locale_must_be_en(self):
        self.assertTrue(any("locale" in d for d in self.run_rule(frontmatter(locale="hi"))))

    def test_title_bounds(self):
        self.assertTrue(any("title length 29" in d for d in self.run_rule(frontmatter(title="T" * 29))))
        self.assertTrue(any("title length 66" in d for d in self.run_rule(frontmatter(title="T" * 66))))
        self.assertEqual(self.run_rule(frontmatter(title="T" * 30)), [])
        self.assertEqual(self.run_rule(frontmatter(title="T" * 65)), [])

    def test_description_bounds(self):
        self.assertTrue(any("description length 109" in d for d in self.run_rule(frontmatter(description="d" * 109))))
        self.assertTrue(any("description length 161" in d for d in self.run_rule(frontmatter(description="d" * 161))))
        self.assertEqual(self.run_rule(frontmatter(description="d" * 160)), [])

    def test_keyword_bounds(self):
        self.assertTrue(self.run_rule(frontmatter(kws=["k"] * 4)))
        self.assertTrue(self.run_rule(frontmatter(kws=["k"] * 9)))
        self.assertEqual(self.run_rule(frontmatter(kws=["k"] * 8)), [])

    def test_author_required(self):
        self.assertTrue(any("author" in d for d in self.run_rule(frontmatter(author=""))))

    def test_living_requires_pubdate(self):
        keys = ["title", "description", "modifiedDate", "locale", "author", "keywords"]
        self.assertTrue(self.run_rule(frontmatter(keys=keys)))

    def test_vastu_pubdate_optional_and_any_date(self):
        keys = ["title", "description", "modifiedDate", "locale", "author", "keywords"]
        self.assertEqual(self.run_rule(frontmatter(keys=keys), require_pubdate=False), [])
        self.assertEqual(self.run_rule(frontmatter(pub="2025-05-08"), require_pubdate=False), [])

    def test_vastu_order_still_checked(self):
        keys = ["title", "description", "modifiedDate", "pubDate", "locale", "author", "keywords"]
        self.assertTrue(self.run_rule(frontmatter(keys=keys), require_pubdate=False))

    def test_date_format(self):
        self.assertTrue(any("pubDate" in d for d in self.run_rule(frontmatter(pub="13 Nov 2026"))))
        self.assertTrue(any("modifiedDate" in d for d in self.run_rule(frontmatter(modified="2026/11/13"))))

    def test_missing_frontmatter(self):
        self.assertTrue(self.run_rule("# Title\n"))


class ValidLivingTests(unittest.TestCase):
    def test_valid_living_article_has_no_problems(self):
        self.assertEqual(a.validate_text(en_article(), Path(LIVING)), [])

    def test_valid_interior_article_has_no_problems(self):
        self.assertEqual(a.validate_text(en_article(), Path(INTERIOR)), [])

    def test_bad_file_name_reported(self):
        out = a.validate_text(en_article(), Path("en/22_Home_Living/2201_Room_by_Room/Bad_Name.mdx"))
        self.assertIn("path", rules(out))


class PlainMarkdownTests(unittest.TestCase):
    def test_jsx_braces_and_links(self):
        for extra in ("<AIBlufSummary>x</AIBlufSummary>", "a { b", "less > more", "see https://example.com",
                      "see http://example.com"):
            out = a.validate_text(en_article(extra=extra), Path(LIVING))
            self.assertIn("plain-markdown", rules(out), extra)


class StructureTests(unittest.TestCase):
    def check(self, text, rel=LIVING):
        return messages(a.validate_text(text, Path(rel)), "structure")

    def test_two_h1(self):
        self.assertTrue(self.check(en_article(extra="# Another title")))

    def test_h1_must_equal_title(self):
        text = en_article().replace(f"# {EN_TITLE}", "# Something else entirely here")
        self.assertTrue(any("title" in m for m in self.check(text)))

    def test_too_few_h2(self):
        self.assertTrue(any("'## '" in m for m in self.check(en_article(h2=4))))
        self.assertEqual(self.check(en_article(h2=5)), [])

    def test_faq_missing(self):
        self.assertTrue(any("FAQ" in m for m in self.check(en_article(faq_heading=None, faq=0, h2=6))))

    def test_faq_question_count(self):
        self.assertTrue(self.check(en_article(faq=3)))
        self.assertTrue(self.check(en_article(faq=7)))
        self.assertEqual(self.check(en_article(faq=6)), [])

    def test_faq_heading_variants(self):
        for h in ("FAQs", "Frequently asked questions", "Common questions"):
            self.assertEqual(self.check(en_article(faq_heading=h)), [], h)

    def test_single_trailing_newline(self):
        self.assertTrue(any("newline" in m for m in self.check(en_article().rstrip("\n"))))
        self.assertTrue(any("newline" in m for m in self.check(en_article() + "\n")))

    def test_vastu_needs_no_five_h2_but_needs_faq(self):
        self.assertEqual(self.check(en_article(h2=2, words=500, measurement=False), VASTU), [])
        self.assertTrue(self.check(en_article(h2=2, words=500, faq=0, faq_heading=None), VASTU))


class LengthTests(unittest.TestCase):
    def length(self, words, rel=LIVING):
        out = a.validate_text(en_article(words=words), Path(rel))
        return ([p[1] for p in out if p[0] == "length" and not p[2]],
                [p[1] for p in out if p[0] == "length" and p[2]])

    def test_word_count_ignores_symbols(self):
        self.assertEqual(a.word_count("| a | b |\n|---|---|\n## Head - x"), 4)

    def test_living_bounds(self):
        self.assertEqual(self.length(900), ([], []))
        self.assertEqual(self.length(1500), ([], []))
        for n in (800, 899, 1501, 1800):
            errs, warns = self.length(n)
            self.assertEqual(errs, [], n)
            self.assertEqual(len(warns), 1, n)
            self.assertIn(str(n), warns[0])
        for n in (799, 1801):
            errs, warns = self.length(n)
            self.assertEqual(len(errs), 1, n)
            self.assertIn(str(n), errs[0])
            self.assertEqual(warns, [], n)

    def test_vastu_minimum_only(self):
        self.assertEqual(len(self.length(399, VASTU)[0]), 1)
        self.assertEqual(self.length(400, VASTU), ([], []))
        self.assertEqual(self.length(5000, VASTU), ([], []))


class MeasurementTests(unittest.TestCase):
    def test_accepted(self):
        for s in ("Leave 75 cm (2 ft 6 in) free.", "A 3.0 x 3.6 m (10 x 12 ft) bedroom.",
                  "Aim for 900 mm (about 3 ft).", "A 150 x 190 cm (5 x 6 ft 3 in) bed.",
                  "75 सेमी (2 फुट 6 इंच) जगह", "3 मीटर (10 फीट) चौड़ा",
                  "75 सेमी (2 फिट 6 इन्च) ठाउँ", "3 मिटर (10 फिट) चौडा",
                  "90 सेन्टिमिटर (3 फिट) बाटो", "74 वर्ग मीटर (800 वर्ग फुट) का फ्लैट",
                  "12 वर्ग मिटर (130 वर्ग फिट) कोठा"):
            self.assertTrue(a.has_metric_with_imperial(s), s)

    def test_rejected(self):
        for s in ("Leave 75 cm free.", "Leave 2 ft 6 in free.", "Leave 5 m (at least) free.", "No numbers."):
            self.assertFalse(a.has_metric_with_imperial(s), s)

    def test_living_article_without_measurement_fails(self):
        out = a.validate_text(en_article(measurement=False), Path(LIVING))
        self.assertIn("measurement", rules(out))

    def test_vastu_article_without_measurement_passes(self):
        out = a.validate_text(en_article(measurement=False), Path(VASTU))
        self.assertNotIn("measurement", rules(out))


class ClaimTests(unittest.TestCase):
    def claims(self, text, rel=LIVING):
        return a.rule_claims(text, Path(rel))

    def assertFlags(self, text, needle, rel=LIVING):
        out = self.claims(text, rel)
        self.assertTrue(any(needle in m for m in out), f"{text!r} -> {out}")

    def test_percentages_near_claim_words(self):
        self.assertFlags("Sales rose 30% after the change.", "rose 30%")
        self.assertFlags("You get a 30% increase in light.", "30% increase")
        self.assertFlags("A 25 percent improvement is common.", "25 percent improvement")
        self.assertFlags("This gives a 12% reduction in heat.", "12% reduction")
        self.assertFlags("Shops saw 40% growth.", "40% growth")
        self.assertFlags("It will boost comfort by 15%.", "boost comfort by 15%")
        self.assertFlags("Expect more customers, perhaps 20% of them.", "more customers, perhaps 20%")

    def test_percentage_far_from_claim_word(self):
        text = "Prices may increase over time. " + "x " * 40 + "Use 10% of the floor for storage."
        self.assertEqual(self.claims(text), [])

    def test_percentage_without_claim_word(self):
        self.assertEqual(self.claims("Keep 10% of the wall free."), [])

    def test_research_phrases(self):
        for s in ("Studies show this works.", "Research shows that.", "research suggests a link.",
                  "Research confirms it.", "It is scientifically proven.", "Science proves this.",
                  "Modern science validates it."):
            self.assertTrue(self.claims(s), s)

    def test_within_period(self):
        self.assertFlags("You will see results within 3 weeks.", "within 3 weeks")
        self.assertFlags("Within six months the room changes.", "Within six months")
        self.assertEqual(self.claims("Keep it within 3 metres of the window."), [])

    def test_guarantee(self):
        self.assertFlags("This layout guarantees a calm home.", "guarantees")
        self.assertFlags("We guarantee good sleep.", "guarantee")
        for s in ("There is no guarantee of this.", "It is not guaranteed.", "Results cannot be guaranteed.",
                  "This is a belief of the tradition, not a guarantee.",
                  "This is not a proven result or a guarantee."):
            self.assertEqual(self.claims(s), [], s)

    def test_negation_in_another_clause_does_not_excuse_guarantee(self):
        self.assertFlags("It is not hard, and it guarantees calm.", "guarantees")
        self.assertFlags("Do not wait. This guarantees calm.", "guarantees")

    def test_ashtakavarga(self):
        self.assertFlags("Unlike Ashtakavarga, this is simple.", "Ashtakavarga", VASTU)
        self.assertFlags("ashtakavarga points", "ashtakavarga", LIVING)
        self.assertEqual(self.claims("Ashtakavarga and Vastu.", ASTRO_VASTU), [])

    def test_currency_in_living_and_interior(self):
        for s, needle in (("It costs Rs 5,000.", "Rs 5,000"), ("About NPR 2000.", "NPR 2000"),
                          ("INR 300 only.", "INR 300"), ("Pay ₹500.", "₹500"), ("Just $20.", "$20"),
                          ("About 4,000 Rs.", "4,000 Rs")):
            self.assertFlags(s, needle, LIVING)
            self.assertFlags(s, needle, INTERIOR)

    def test_currency_allowed_in_vastu(self):
        self.assertEqual(self.claims("It costs Rs 5,000.", VASTU), [])

    def test_claims_reported_as_errors_in_validate_text(self):
        out = a.validate_text(en_article(extra="Studies show this."), Path(LIVING))
        self.assertIn("claims", rules(out))


class LocaleTests(unittest.TestCase):
    def check(self, text, rel=HI_LIVING, english=None):
        if english is None:
            english = en_article(words=1000)
        return a.validate_text(text, Path(rel), english_text=english)

    def test_valid_hindi(self):
        self.assertEqual(self.check(hi_article(words=700)), [])

    def test_missing_english_source(self):
        out = a.validate_text(hi_article(), Path(HI_LIVING), english_text=None)
        self.assertIn("source", rules(out))

    def test_length_ratio(self):
        out = self.check(hi_article(words=640))
        self.assertTrue(any("0.64" in m for m in messages(out, "length")))
        self.assertEqual(messages(self.check(hi_article(words=650)), "length"), [])

    def test_source_locale_required(self):
        out = self.check(hi_article(source=None))
        self.assertIn("frontmatter", rules(out))

    def test_locale_must_match_folder(self):
        out = self.check(hi_article(locale="ne"))
        self.assertIn("frontmatter", rules(out))

    def test_devanagari_digits_rejected(self):
        out = self.check(hi_article(extra="कमरा ७५ सेमी है।"))
        self.assertTrue(any("digit" in m for m in messages(out, "script")))

    def test_latin_heavy_body_rejected(self):
        out = self.check(hi_article(extra="this paragraph is written in plain english " * 80))
        self.assertIn("script", rules(out))

    def test_template_phrase(self):
        out = self.check(hi_article(extra="Executive Summary"))
        self.assertIn("template", rules(out))

    def test_hindi_text_in_nepali_folder(self):
        out = self.check(hi_article(locale="ne"), rel=NE_LIVING)
        self.assertIn("language", rules(out))

    def test_structure_rules_apply(self):
        out = self.check(hi_article().replace("## अक्सर पूछे जाने वाले प्रश्न", "## अंत"))
        self.assertIn("structure", rules(out))

    def test_measurement_rule_applies(self):
        out = self.check(hi_article().replace("75 सेमी (2 फुट 6 इंच)", "75 सेमी"))
        self.assertIn("measurement", rules(out))

    def test_pubdate_must_match_english(self):
        out = self.check(hi_article(pub="2026-12-01"))
        self.assertTrue(any("pubDate" in m for m in messages(out, "frontmatter")))


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class FindFilesTests(unittest.TestCase):
    def test_filters(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for rel in (LIVING, INTERIOR, VASTU, HI_LIVING, NE_LIVING,
                        "en/18_Vastu/Directions_Docs/x.mdx", "en/22_Home_Living/_meta.json",
                        "hi/18_Vastu/1803_Directions/180301_East_Direction.mdx", "en/01_Rasi/A/x.mdx"):
                write(root, rel, "x")

            def names(**kw):
                return sorted(str(p.relative_to(root)) for p in a.find_files(root, **kw))

            self.assertEqual(names(), sorted([LIVING, INTERIOR, VASTU, HI_LIVING, NE_LIVING]))
            self.assertEqual(names(locale="hi"), [HI_LIVING])
            self.assertEqual(names(topic="18_Vastu"), [VASTU])
            self.assertEqual(names(locale="en", topic="22_Home_Living"), [LIVING])
            self.assertEqual(names(section="2301_Layout_and_Furniture"), [INTERIOR])


class CliTests(unittest.TestCase):
    def run_main(self, root, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = a.main(argv, root=root)
        return code, buf.getvalue()

    def test_silent_when_all_pass(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            write(root, LIVING, en_article())
            write(root, HI_LIVING, hi_article())
            code, out = self.run_main(root, [])
            self.assertEqual((code, out), (0, ""))

    def test_problem_lines_and_exit_code(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            write(root, LIVING, en_article(extra="Studies show this."))
            write(root, INTERIOR, en_article())
            code, out = self.run_main(root, [])
            self.assertEqual(code, 1)
            self.assertIn(f"{LIVING}: claims: ", out)
            self.assertNotIn(INTERIOR, out)

    def test_explicit_file_and_missing_source(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = write(root, HI_LIVING, hi_article())
            code, out = self.run_main(root, [str(p)])
            self.assertEqual(code, 1)
            self.assertIn(f"{HI_LIVING}: source: ", out)

    def test_warning_only_exits_zero(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            write(root, LIVING, en_article(words=850))
            code, out = self.run_main(root, [])
            self.assertEqual(code, 0)
            self.assertIn(f"{LIVING}: length: warning: ", out)

    def test_summary(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            write(root, LIVING, en_article(extra="Studies show this."))
            write(root, INTERIOR, en_article())
            code, out = self.run_main(root, ["--summary"])
            self.assertEqual(code, 1)
            self.assertIn("claims: 1", out)
            self.assertIn("files checked: 2; passing: 1; failing: 1", out)

    def test_unsupported_topic_for_file(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = write(root, "hi/18_Vastu/1803_Directions/180301_East_Direction.mdx", hi_article())
            code, out = self.run_main(root, [str(p)])
            self.assertEqual(code, 1)
            self.assertIn("path: ", out)


if __name__ == "__main__":
    unittest.main()
