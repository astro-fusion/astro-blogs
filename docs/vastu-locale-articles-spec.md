# Vastu articles in Hindi and Nepali: writing spec

Owner decision, 12 Nov 2026: the Hindi and Nepali files under `hi/18_Vastu` and `ne/18_Vastu` were one generic template repeated 187 times per language. Each is replaced by a real article written from its English source. These files are published at `vastu.astro-fusion.com/{hi,ne}/articles/vastu/<section>/<slug>`.

## Source and target

- Source: `en/18_Vastu/<section folder>/<file>.mdx`.
- Target: the file at the same path under `hi/` or `ne/`. Overwrite it completely. Never rename, move, add or delete files; the URL is built from the path.

## What to carry over from the English article

Translate and adapt the real content, section by section, in the same order:

- Keep: Introduction, "What is …", Key Aspects, Calculation Method, Interpretation Guidelines, Practical Applications, Common Misconceptions, Examples, Conclusion, FAQs, and any other real content section.
- Drop: `## Keywords`, `## Resources` (a list of other websites), `## Classical Sanskrit Shastra Citation`, `## Previous Article`, `## Next Article`.
- Drop every JSX component: `<AIBlufSummary>`, `<KundaliChart>`, `<BookShlokaSnippet>`, `<YogaDeepLink>` and any other tag. The target file is plain Markdown only. If an `<AIBlufSummary>` holds a real summary of the article (not a list of websites), write its content as an ordinary paragraph.
- Keep every fact, number, direction, measurement, list item and table of the retained sections. Do not shorten into a summary.
- Do not add facts, statistics, case studies, scripture verses, chapter or verse numbers, or sources that are not in the English article. Never write a Sanskrit shloka from memory.
- Where the English text is plainly padded or repeats itself, say it once.

## Editorial clean-up (added after the pilot, 12 Nov 2026)

The English articles were generated from an astrology template and carry its leftovers. Do not carry these into the target; the target must read as an article about Vastu only.

- **Template leakage.** Remove every mention of Ashtakavarga and any comparison with "other aspects" of an astrology system, unless the article's own topic is astrology with Vastu (section `1808_Astro-Vastu…`). Remove sentences addressed to "astrology enthusiasts and practitioners" that say nothing about the topic.
- **Generic FAQs.** Questions such as "How does X differ from other aspects of Ashtakavarga?", "Can X be used for prediction?", "Do I need my exact birth time?" are template questions. Replace the FAQ section with 4 to 6 questions a home owner would ask about this article's topic, each answered only from what the article itself says.
- **Boilerplate sections.** If "Calculation Method" or "Interpretation Guidelines" in the English says nothing specific to the topic, fold its one or two useful points into the nearest real section and drop the heading. Give kept sections a heading that fits the content (for example "दिशा कैसे तय करें" instead of a literal "गणना की विधि").
- **Numbers without a source.** Drop invented-looking statistics and anonymous success stories with figures ("30% more customers in 3 months", "23% rise in satisfaction", "research suggests…" with no study named). An example may stay as a plain illustration without the figures. Real, checkable numbers stay: dimensions, angles, the 32 zones, the 45 deities, dates of well-known texts and monuments.
- **Tradition stated as tradition.** Write what Vastu tradition holds as tradition ("वास्तु परंपरा के अनुसार", "वास्तु परम्पराअनुसार"), not as proven science or medicine. Never promise health, wealth or cures.
- **History.** Keep historical statements the English makes, but do not strengthen them; where the English presents a contested claim as fact (for example a monument "built on Vastu"), say that it is often cited as an example.
- **Citation markers.** Drop `[1]`, `[2]` style markers.
- **Contradictions.** If the article contradicts itself or a basic Vastu fact (for example the element of a direction), do not resolve it by guessing: follow the standard association (earth south-west, water north-east, fire south-east, air north-west, space centre) and list the article in your report.

- **Known slips in the English.** Where the English states one of these, write the standard version and list the article in your report: ground and water should slope towards the north-east (not south-east); the Vastu Purusha Mandala has 45 deities (Brahma at the centre, 12 in the inner ring, 32 on the perimeter); Hastinapur and Indraprastha belong to the Dvapara age (not Kali); Lanka is said to have been built by Vishwakarma for Kubera. For any other statement you believe is wrong but cannot be sure of, soften it ("माना जाता है", "भनिन्छ") or leave it out, and list it; never replace it with a new specific claim.
- **Truncated source.** If the English breaks off mid-sentence, stop at the last complete point.
- **Title and content.** The title must describe what the article actually covers, even if the file name promises more.

After this clean-up the length rule applies to what is left: at least 65% of the words of the English content you actually kept.

## Length

The target body must have at least 65% as many words as the retained English sections. A short English article gives a short target; never pad.

## Language

- Hindi: modern standard Hindi in Devanagari, the register of a good newspaper feature. Nepali: standard Nepali in Devanagari. Nepali is not Hindi with changed endings; use Nepali vocabulary and grammar (छ, हुन्छ, गर्नुहोस्, तपाईंको, र, पनि).
- Write for a home owner, not a scholar. Short sentences. No English sentences left untranslated.
- Technical terms: use the term people actually use. Sanskrit Vastu terms stay in Devanagari (वास्तु पुरुष मण्डल, ईशान कोण, ब्रह्मस्थान). For an engineering or modern term with no common equivalent, give the Devanagari form and the English once in brackets on first use, for example "भार वहन क्षमता (bearing capacity)".
- Directions: use the traditional names with the plain direction on first use, for example "ईशान (उत्तर-पूर्व)".
- Numerals: Latin digits (1, 2, 3) in both languages, so measurements read the same everywhere.
- No file-name artefacts: never write underscores or "East Direction_Purva_in Vastu" style strings.

## Format

Frontmatter, exactly these keys in this order:

```yaml
---
title: "<natural title in the target language, 30 to 65 characters, no underscores>"
description: "<one or two sentences in the target language, 110 to 160 characters>"
pubDate: '<copy from the English file>'
modifiedDate: '2026-11-12'
locale: '<hi or ne>'
sourceLocale: 'en'
author: 'AstroFusion Editorial'
keywords:
  - "<5 to 8 search phrases in the target language>"
---
```

- Use double quotes for title, description and keywords; do not put a double quote inside them.
- Body: one `# ` heading equal to the title, then `## ` sections and `### ` subsections. Lists and Markdown tables are fine.
- FAQs: a `## ` heading for the FAQ section, each question as `### `, the answer as a paragraph.
- MDX safety: no `<`, `>`, `{` or `}` characters anywhere in the body. Write "से कम" / "भन्दा कम" instead of `<`.
- No links to other websites. No "Previous / Next" lines.
- End the file with one newline.

## Check before you finish each file

1. Every retained English section has its counterpart, in order.
2. No JSX, no braces, no angle brackets, no underscores in the title.
3. The text reads as natural Hindi or Nepali when read aloud.
4. Run `python3 scripts/validate_vastu_locale.py <file>` if the script exists, and fix what it reports.

## More editorial rules (from the pilot reports)

- No remedy that costs money or carries risk stated as advice: drop gemstone prescriptions (for example blue sapphire for Saturn) and paid rituals; a remedy may be described as a traditional practice, never recommended.
- Drop claims that Vastu "aligns with quantum physics" or that "scientific studies show" a benefit when no study is named.
- Drop a sentence that leads into a formula or list that is missing in the English.
- A building is described as what it is (the Taj Mahal is a mausoleum, not a temple).
