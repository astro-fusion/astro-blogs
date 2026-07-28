# AGENT HANDOVER — Interactive Kundali Chart Embedding Task

> **This file is the single source of truth for an AI agent running this task.**
> Read it fully before processing any blog file. It contains the complete spec, the component API, the decision logic, and the progress tracker.

---

## 1. Mission Summary

**Goal**: Enhance every blog post in the `06_Planet_in_Houses/` and `10_Lord_in_Houses/` directories (279 files) by embedding an interactive `<KundaliChart />` React component that visually illustrates the specific planetary combination being discussed.

**Why**: These posts rank for high-intent SEO queries like:
- "8th lord in 2nd house" (13 clicks / 196 impressions)
- "2nd lord in 8th house" (6 clicks / 251 impressions)
- "Sun in 1st house", "Moon in 5th house", etc.

Users search for these topics wanting to **see** the chart. An embedded visual keeps users on-page longer, reduces bounce rate, and increases Kundali calculator conversions.

**Non-goal**: Do NOT touch files in `01_Rasi`, `02_Houses`, `03_Planets`, `05_Nakshatra`, `21_Numerology`, `18_Vastu`, `04_DashaSystem`, `20_Transit` etc. Those categories don't benefit from this specific component.

---

## 2. The `<KundaliChart />` Component — Complete API Reference

This component is pre-registered in the AstroFusion MDX pipeline and works out-of-the-box in any `.mdx` file in this repository. You do NOT need to import it.

### Props

```tsx
<KundaliChart
  title="..."              // string — Card title (right panel)
  description="..."        // string — Explanation paragraph
  combinationLabel="..."   // string — Short badge label (e.g. "Sun in 1st House")
  lagnaRashi={1}           // number — Ascendant rasi 1=Aries, 2=Taurus ... 12=Pisces
  placements={[...]}       // PlacementProp[] — Planet positions (see below)
  highlightHouses={[1,5]}  // number[] — Houses to show callout badges for (max 4)
  effects={[...]}          // string[] — Bullet points in "Key Dynamics" panel
  ctaText="..."            // string — CTA button label
  ctaHref="/kundali"       // string — CTA button link (always /kundali)
/>
```

### PlacementProp

```ts
{
  planet: string;    // Planet name: "Sun" | "Moon" | "Mars" | "Mercury" | "Jupiter" | "Venus" | "Saturn" | "Rahu" | "Ketu"
  house: number;     // House number 1–12 (Bhava position in the chart)
  isLordOf?: number; // Optional: which house this planet is lord of (for labelling)
}
```

### Aliases (all three work identically)
```mdx
<KundaliChart ... />             ← recommended
<KundaliIllustration ... />      ← alias
<BlogInteractiveKundaliChart ... /> ← full name
```

### lagnaRashi Reference

| lagnaRashi | Sign | Sanskrit |
|---|---|---|
| 1 | Aries | Mesha |
| 2 | Taurus | Vrishabha |
| 3 | Gemini | Mithuna |
| 4 | Cancer | Karka |
| 5 | Leo | Simha |
| 6 | Virgo | Kanya |
| 7 | Libra | Tula |
| 8 | Scorpio | Vrishchika |
| 9 | Sagittarius | Dhanu |
| 10 | Capricorn | Makara |
| 11 | Aquarius | Kumbha |
| 12 | Pisces | Meena |

---

## 3. Planet-in-House Pattern (06_Planet_in_Houses)

### Rule for All "Planet in House N" Articles

For a "Sun in 3rd House" article, the chart should show the Sun in house 3.

**lagnaRashi selection**: Use **Aries Lagna (lagnaRashi=1)** as the default illustrative lagna for all Planet-in-House articles. This is the most neutral and universally understood lagna for illustrations.

**Template** (replace `{PLANET}`, `{HOUSE_NUMBER}`):

```mdx
<KundaliChart
  title="{PLANET} in {HOUSE_NUMBER}th House — Chart Illustration"
  combinationLabel="{PLANET} in {HOUSE_NUMBER}th House"
  lagnaRashi={1}
  placements={[
    { planet: "{PLANET}", house: {HOUSE_NUMBER} }
  ]}
  highlightHouses={[{HOUSE_NUMBER}]}
  description="This illustrative chart shows {PLANET} placed in the {HOUSE_NUMBER}th house (Bhava) for an Aries Lagna. The exact effects depend on your personal chart — use the Kundali calculator to see your placement."
  effects={[
    "See the specific section below for detailed effects by sign and lagna.",
    "{PLANET} here activates the themes of the {HOUSE_NUMBER}th house throughout its dasha period.",
    "The degree, conjunctions, and aspects to {PLANET} further modify these results."
  ]}
  ctaText="See {PLANET} in Your Chart"
  ctaHref="/kundali"
/>
```

**Insertion point**: Place AFTER the Summary/AIBlufSummary section and BEFORE the first major H2 subheading (##). This gives users a visual anchor before the detailed text.

### Special Case: Planet in 1st House (Lagna)

For "Sun in 1st House", "Moon in Lagna" etc., use:
```mdx
<KundaliChart
  title="Sun in Lagna (1st House)"
  combinationLabel="Sun in Lagna"
  lagnaRashi={5}
  placements={[{ planet: "Sun", house: 1 }]}
  highlightHouses={[1]}
  ...
/>
```
Use `lagnaRashi=5` (Leo) for Sun-in-Lagna illustration since Sun rules Leo — visually informative.

### Planet-to-Lagna Mapping for "Planet in 1st House" Articles

| Planet | Best lagnaRashi | Reason |
|---|---|---|
| Sun | 5 (Leo) | Sun rules Leo |
| Moon | 4 (Cancer) | Moon rules Cancer |
| Mars | 1 (Aries) | Mars rules Aries |
| Mercury | 3 (Gemini) | Mercury rules Gemini |
| Jupiter | 9 (Sagittarius) | Jupiter rules Sagittarius |
| Venus | 2 (Taurus) | Venus rules Taurus |
| Saturn | 10 (Capricorn) | Saturn rules Capricorn |
| Rahu | 1 (Aries) | Generic; use Aries |
| Ketu | 1 (Aries) | Generic; use Aries |

For all other houses (2nd–12th), always use `lagnaRashi=1` (Aries).

---

## 4. House Lord Pattern (10_Lord_in_Houses)

### Rule for All "Nth Lord in Mth House" Articles

For a "8th Lord in 2nd House" article:
- Planet in house 2 = the 8th lord (use a representative planet as 8th lord)
- Highlight houses [2, 8] to show the axis

**lagnaRashi selection**: Use **Aries Lagna (lagnaRashi=1)** by default. Then the 8th lord = Mars (Scorpio in 8th from Aries). Use Mars as the planet for Aries lagna examples.

### Lord-to-Planet Mapping (Aries Lagna / lagnaRashi=1)

| House Lord | Natural Ruler (Aries Lagna) | Sign Ruled |
|---|---|---|
| 1st lord | Mars | Aries |
| 2nd lord | Venus | Taurus |
| 3rd lord | Mercury | Gemini |
| 4th lord | Moon | Cancer |
| 5th lord | Sun | Leo |
| 6th lord | Mercury | Virgo |
| 7th lord | Venus | Libra |
| 8th lord | Mars | Scorpio |
| 9th lord | Jupiter | Sagittarius |
| 10th lord | Saturn | Capricorn |
| 11th lord | Saturn | Aquarius |
| 12th lord | Jupiter | Pisces |

**Template** (replace `{N}` = lord's house, `{M}` = target house, `{PLANET}` = planet from table above):

```mdx
<KundaliChart
  title="{N}th Lord in {M}th House — Illustrative Chart"
  combinationLabel="{N}th Lord in {M}th House"
  lagnaRashi={1}
  placements={[
    { planet: "{PLANET}", house: {M}, isLordOf: {N} }
  ]}
  highlightHouses={[{N}, {M}]}
  description="This illustrative chart (Aries Lagna) shows the {N}th lord placed in the {M}th house. For Aries Lagna, {PLANET} rules the {N}th house and is placed here in the {M}th. Your actual {N}th lord depends on your personal Lagna — calculate your Kundali for precise results."
  effects={[
    "{N}th house themes (see table) are activated in the domain of the {M}th house.",
    "The planet's natural significations blend with both house meanings.",
    "Dasha and Antardasha of this lord intensifies this placement's effects."
  ]}
  ctaText="Find Your {N}th Lord Placement"
  ctaHref="/kundali"
/>
```

**Parivartana Yoga Case**: When the article is about "2nd Lord in 8th House" AND the reciprocal "8th Lord in 2nd House" is mentioned, add a SECOND `<KundaliChart />` showing BOTH planets for the exchange:

```mdx
<KundaliChart
  title="Parivartana Yoga — 2nd & 8th House Exchange"
  combinationLabel="2nd Lord ↔ 8th Lord Exchange"
  lagnaRashi={1}
  placements={[
    { planet: "Venus", house: 8, isLordOf: 2 },
    { planet: "Mars", house: 2, isLordOf: 8 }
  ]}
  highlightHouses={[2, 8]}
  description="When the 2nd lord is in the 8th AND the 8th lord is in the 2nd, a Parivartana Yoga (mutual exchange) forms. This dramatically amplifies both wealth and transformation themes."
  effects={[
    "Parivartana between 2nd and 8th creates extreme financial cycles.",
    "Hidden income or sudden wealth through partner's resources is possible.",
    "The native may alternate between great accumulation and sudden loss."
  ]}
  ctaText="Check for Parivartana in Your Chart"
  ctaHref="/kundali"
/>
```

---

## 5. House Signification Reference (for `highlightHouses` badges)

When choosing `highlightHouses`, pick the most relevant 1–4 houses to the article topic:

| House | Significations | Element |
|---|---|---|
| 1 | Self, identity, body, appearance, lagna | Fire |
| 2 | Wealth, family, speech, food, eyes, teeth | Earth |
| 3 | Siblings, courage, communication, short travel | Air |
| 4 | Home, mother, property, education, comforts | Water |
| 5 | Intellect, children, creativity, romance, speculation | Fire |
| 6 | Enemies, debts, disease, service, competition | Earth |
| 7 | Marriage, partnerships, business, foreign travel | Air |
| 8 | Longevity, transformation, hidden wealth, occult | Water |
| 9 | Dharma, fortune, father, higher learning, religion | Fire |
| 10 | Career, fame, public life, authority, status | Earth |
| 11 | Gains, friends, elder siblings, aspirations | Air |
| 12 | Liberation, losses, foreign lands, hospitals, expenses | Water |

---

## 6. SEO Best Practices — Mandatory for Every File

When touching any file, also audit and improve these:

### 6.1 Frontmatter (YAML)

**Required fields**:
```yaml
---
title: 'Exact keyword phrase — Supporting detail'
description: >
  150-160 char meta description with primary keyword in first 60 chars.
  Should be a complete sentence that entices clicks.
pubDate: '2024-08-01'
keywords:
  - primary keyword (exact match)
  - secondary keyword variant 1
  - secondary keyword variant 2
  - vedic astrology
  - jyotish
  - kundali
modifiedDate: '2026-07-28'   ← ADD THIS on every file you touch
---
```

**Title rules**:
- Must contain the exact keyword from GSC (e.g. "8th lord in 2nd house")
- Max 60 characters for SERPs, can be longer for rich results
- Use `:` or `—` to add supporting detail after main keyword
- Avoid stuffing; one primary keyword per title

**Description rules**:
- 150-160 chars (Google truncates beyond 160)
- Primary keyword in first 60 chars
- Action-oriented: "Discover", "Learn", "Explore", "Understand"
- Includes secondary benefit: effects, remedies, meaning, calculation

### 6.2 Content Headings (H1/H2/H3)

- **H1**: Match the primary keyword closely. One H1 per file.
- **H2**: Include semantic variations of the keyword:
  - "What is 8th Lord in 2nd House?"
  - "Effects of 8th Lord in 2nd House"
  - "8th Lord in 2nd House — Lagna by Lagna"
  - "Remedies for 8th Lord in 2nd House"
- **H3**: Use conversational questions matching "People Also Ask":
  - "Is 8th lord in 2nd house good or bad?"
  - "What does it mean when your 8th lord is in 2nd house?"

### 6.3 FAQ Section — MANDATORY

Every file MUST have a `<FAQBlock>` component with 4–6 questions. These directly target Google's "People Also Ask" box.

```mdx
<FAQBlock
  faqs={[
    {
      question: "Is 8th lord in 2nd house good or bad?",
      answer: "It is a complex placement — neither purely good nor bad. It brings wealth through non-conventional means like inheritance, joint assets, or occult services, but also creates financial fluctuations. The exact planet acting as 8th lord and its dignity significantly influence the outcome."
    },
    {
      question: "What does 8th lord in 2nd house mean in Vedic astrology?",
      answer: "It means the ruling planet of the 8th house (transformation, hidden wealth, longevity) is placed in the 2nd house (wealth, family, speech). This creates a merging of 8th-house themes into 2nd-house matters — wealth arrives through unexpected channels, family life undergoes transformation."
    },
    {
      question: "Which planet is 8th lord for Aries lagna?",
      answer: "For Aries Lagna (Mesha), Mars rules both Aries (1st house) and Scorpio (8th house). So Mars is the 8th lord. When Mars sits in the 2nd house (Taurus), it brings Scorpionic intensity to wealth and speech matters."
    },
    {
      question: "Does 8th lord in 2nd house give inheritance?",
      answer: "Yes, this is one of the classic indicators of inheritance in Vedic astrology. The 8th house governs other people's money, legacies, and estates, while the 2nd house represents personal wealth. Their connection often manifests as gains through inheritance, insurance, or a partner's resources."
    }
  ]}
/>
```

### 6.4 Internal Linking (Cross-linking / Inbound)

**Every file must link to at least 3–5 related articles.** Use this standard Related Articles section at the END of every post:

```mdx
---

## Related Articles

- [Nth Lord in Mth House](/blogs/100N_Nth_Lord_in_all_Houses/100NM_Nth_Lord_in_Mth_House)
- [Mth Lord in Nth House](/blogs/100M_Mth_Lord_in_all_Houses/100MN_Mth_Lord_in_Nth_House) — the reciprocal exchange
- [Understanding the Nth House in Vedic Astrology](/blogs/02_Houses/20N_Nth_House_in_Vedic_Astrology)
- [Planet X in House N Overview](/blogs/06_Planet_in_Houses/...)
- [Parivartana Yoga Explained](/blogs/12_Articles/...)
```

**Linking Rules**:
1. **Reciprocal exchange**: If editing "8th lord in 2nd", always link to "2nd lord in 8th" and vice versa
2. **House articles**: Link to the house overview article for each highlighted house
3. **Planet articles**: Link to the planet's overview article
4. **Category sibling**: Link to the "Overview" or "All Houses" article in the same folder (e.g. `100800_8th_Lord_in_all_12_Houses.mdx`)
5. **Kundali CTA**: The `<KundaliChart />` component already includes the CTA — do NOT add a separate redundant CTA paragraph

### 6.5 AIBlufSummary — Update if Stale

If the file has an `<AIBlufSummary>` block, update it to be:
- 2–3 sentences maximum
- Directly answers the primary query intent (informational / navigational)
- Contains the primary keyword naturally
- Mentions the CTA lightly ("Calculate your Kundali to see your personal placement")

---

## 7. Step-by-Step Agent Workflow — Per File

For each `.mdx` file in scope, follow these steps **in order**:

### Step 1: Read and Parse
- Read the full file
- Extract: planet name (if Planet-in-House), lord number + target house (if Lord-in-House)
- Identify current state: does it have `<KundaliChart>`? FAQ? Related Articles?

### Step 2: Determine Chart Props
- Use Section 3 (Planet-in-House) or Section 4 (Lord-in-House) to determine:
  - `lagnaRashi` value
  - `placements` array (planet + house)
  - `highlightHouses` array
  - `effects` array (derive from article content — pick 3–4 key points)

### Step 3: Find Insertion Point
- Insert `<KundaliChart />` AFTER the opening summary / `<AIBlufSummary>` block
- BEFORE the first `##` subheading
- If no `<AIBlufSummary>` exists, insert after the first paragraph

### Step 4: SEO Audit
- Check `title` — does it contain the exact keyword? Fix if not.
- Check `description` — is it 150-160 chars with keyword in first 60? Fix if not.
- Check `keywords` array — does it include modern keyword variants? Add missing ones.
- Add `modifiedDate: '2026-07-28'` to frontmatter.

### Step 5: Add FAQ Block
- If no `<FAQBlock>` exists, add one with 4 questions before the Related Articles section
- Follow the pattern in Section 6.3

### Step 6: Add/Update Related Articles
- Ensure a Related Articles section exists at the bottom
- Add at minimum: reciprocal article + house overview + category sibling

### Step 7: Write the File
- Make ALL changes in a single write (not incremental patches)
- Do NOT change the article body content structure (H2s, paragraphs, lists)
- Do NOT remove existing `<AIBlufSummary>`, `<TipBlock>`, `<WarningBlock>` etc.
- Preserve all existing content; only ADD the new elements

### Step 8: Mark Progress (update this file)
- Update the progress tracker below: change `[ ]` → `[x]` for the completed file

---

## 8. Priority Order (by SEO impact / GSC impressions)

Process files in this order — highest-impact first:

### BATCH 1 — Lord-in-Houses (GSC top queries)
| Priority | File | Keyword | Status |
|---|---|---|---|
| 🔴 HIGH | `10_Lord_in_Houses/1008_8th_Lord_in_all_Houses/100802_8th_Lord_in_2nd_House.mdx` | 8th lord in 2nd house | [x] |
| 🔴 HIGH | `10_Lord_in_Houses/1002_2nd_Lord_in_all_Houses/100208_2nd_Lord_in_8th_House.mdx` | 2nd lord in 8th house | [x] |
| 🔴 HIGH | `10_Lord_in_Houses/1001_1st_Lord_in_all_Houses/100112_1st_Lord_in_1nd_House.mdx` | 1st lord in 12th house | [x] |
| 🟠 MED | `10_Lord_in_Houses/1008_8th_Lord_in_all_Houses/100800_8th_Lord_in_all_12_Houses.mdx` | 8th lord in houses | [x] |
| 🟠 MED | `10_Lord_in_Houses/1002_2nd_Lord_in_all_Houses/100202_2nd_Lord_in_2nd_House.mdx` | 2nd lord in 2nd house | [x] |

### BATCH 2 — Sun in Houses (Planet-in-Houses)
| Priority | File | Keyword | Status |
|---|---|---|---|
| 🔴 HIGH | `06_Planet_in_Houses/0601_Sun_in_Houses/060101_Sun_in_11th_House.mdx` | Sun in 1st house / lagna | [x] |
| 🟠 MED | `06_Planet_in_Houses/0601_Sun_in_Houses/060102_Sun_in_2nd_House.mdx` | Sun in 2nd house | [x] |
| 🟠 MED | `06_Planet_in_Houses/0601_Sun_in_Houses/060104_Sun_in_4th_House.mdx` | Sun in 4th house | [x] |
| 🟠 MED | `06_Planet_in_Houses/0601_Sun_in_Houses/060105_Sun_in_5th_House.mdx` | Sun in 5th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060108_Sun_in_8th_House.mdx` | Sun in 8th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060107_Sun_in_7th_House.mdx` | Sun in 7th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060110_Sun_in_10th_House.mdx` | Sun in 10th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060103_Sun_in_3rd_House.mdx` | Sun in 3rd house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060106_Sun_in_6th_House.mdx` | Sun in 6th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060109_Sun_in_9th_House.mdx` | Sun in 9th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060111_Sun_in_11th_House.mdx` | Sun in 11th house | [x] |
| 🟡 LOW | `06_Planet_in_Houses/0601_Sun_in_Houses/060112_Sun_in_1nd_House.mdx` | Sun in 12th house (filename: 1nd) | [x] |

### BATCH 3 — Moon in Houses
| Priority | File | Keyword | Status |
|---|---|---|---|
| 🔴 HIGH | `06_Planet_in_Houses/0602_Moon_in_Houses/060201_Moon_in_11th_House.mdx` | Moon in lagna (filename quirk) | [x] |
| 🟠 MED | `06_Planet_in_Houses/0602_Moon_in_Houses/060204_Moon_in_4th_House.mdx` | Moon in 4th house | [x] |
| 🟠 MED | `06_Planet_in_Houses/0602_Moon_in_Houses/060205_Moon_in_5th_House.mdx` | Moon in 5th house | [x] |
| 🟡 LOW | All remaining Moon files (2nd–3rd,6th–12th) | | [x] |

### BATCH 4 — All Remaining Lord-in-Houses (144 files total, all 12 lords × 12 houses)
Process the full `10_Lord_in_Houses/` directory folder by folder:
- [ ] `1001_1st_Lord_in_all_Houses` (12 files)
- [ ] `1002_2nd_Lord_in_all_Houses` (12 files)
- [ ] `1003_3rd_Lord_in_all_Houses` (12 files)
- [ ] `1004_4th_Lord_in_all_Houses` (12 files)
- [ ] `1005_5th_Lord_in_all_Houses` (12 files)
- [ ] `1006_6th_Lord_in_all_Houses` (12 files)
- [ ] `1007_7th_Lord_in_all_Houses` (12 files)
- [ ] `1008_8th_Lord_in_all_Houses` (12 files)
- [ ] `1009_9th_Lord_in_all_Houses` (12 files)
- [ ] `1010_10th_Lord_in_all_Houses` (12 files)
- [ ] `1011_11th_Lord_in_all_Houses` (12 files)
- [ ] `1012_12th_Lord_in_all_Houses` (12 files)

### BATCH 5 — All Remaining Planet-in-Houses (Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- [ ] `0603_Mars_in_Houses` (12 files)
- [ ] `0604_Mercury_in_Houses` (12 files)
- [ ] `0605_Jupiter_in_Houses` (12 files)
- [ ] `0606_Venus_in_Houses` (12 files)
- [ ] `0607_Saturn_in_Houses` (12 files)
- [ ] `0608_Rahu_in_Houses` (12 files)
- [ ] `0609_Ketu_in_Houses` (12 files)

---

## 9. Parivartana Yoga — Special Article List

These pairs have a mutual exchange (Parivartana Yoga). Both articles in each pair MUST:
1. Have `<KundaliChart />` showing the exchange (both planets in both houses)
2. Link to each other prominently
3. Mention the Parivartana Yoga with the `<InfoBlock>` component

**High-priority pairs** (GSC data):
- 2nd lord ↔ 8th lord (2nd in 8th / 8th in 2nd) 🔴
- 1st lord ↔ 7th lord 🟠
- 5th lord ↔ 9th lord (Dharma-Trikona exchange) 🟠
- 4th lord ↔ 10th lord (Kendra axis) 🟠

---

## 10. Component Placement Rules — Visual Guide

### Single-planet article (Planet in House):
```
[Frontmatter]
# H1 Heading

Opening paragraph.

<AIBlufSummary>...</AIBlufSummary>

<KundaliChart ... />    ← INSERT HERE

## First Major Section
...
[body content — DO NOT touch]
...
<FAQBlock ... />        ← ADD if missing
---
## Related Articles     ← ADD if missing
- links
```

### Lord-in-House article:
```
[Frontmatter]
# H1 Heading

<AIBlufSummary>...</AIBlufSummary>

<KundaliChart ... />           ← INSERT HERE (lord placement)

## Core Effects
...
[body — DO NOT touch]
...

<KundaliChart ... />           ← OPTIONAL 2nd chart if Parivartana
(only for the 2nd/8th, 1st/7th pairs etc.)

<FAQBlock ... />               ← ADD if missing
---
## Related Articles            ← ADD if missing
```

---

## 11. Quality Checklist — Before Marking a File Complete

- [ ] `<KundaliChart />` embedded with correct planet, house, lagnaRashi
- [ ] `highlightHouses` matches the houses discussed in the article
- [ ] `effects` are derived from actual article content (not generic)
- [ ] Frontmatter `title` contains exact primary keyword
- [ ] Frontmatter `description` is 150-160 chars with keyword in first 60 chars
- [ ] `modifiedDate: '2026-07-28'` added to frontmatter
- [ ] `<FAQBlock />` present with 4+ question-answer pairs
- [ ] Related Articles section present with 3+ internal links
- [ ] No content removed — only additions/improvements
- [ ] File saved as `.mdx` (not `.md`)

---

## 12. Error Handling

If you encounter a file where you cannot determine the planet or house from the filename:

1. Read the file's H1 heading and frontmatter title
2. Extract planet/house from the title text
3. If still ambiguous, skip and mark with `[SKIP]` in the tracker with a note

Common filename quirks in this repo:
- `060112_Sun_in_1st_House.mdx` → "1nd" = 1st (typo in filenames, should be "1st")
- `100801_8th_Lord_in_11th_House.mdx` and `100811_8th_Lord_in_11th_House.mdx` → check file content for which house is actually covered (known duplicate filenames)

---

## 13. Technical Notes

### The `<KundaliChart />` component is hosted in the AstroFusion Next.js app, NOT in this repo.

This repo (astro-blogs) is the **content** layer. The component is registered in:
`apps/web/astro-fusion/src/app/[locale]/blogs/components/mdx/custom-components.tsx`

You (agent) only need to write the MDX syntax — the platform handles rendering.

### MDX Syntax Rules
- Props with string values: `title="..."`  
- Props with numbers: `lagnaRashi={1}` (curly braces, no quotes)
- Props with arrays: `placements={[{ planet: "Sun", house: 1 }]}`
- Props with arrays of strings: `effects={["...", "..."]}`
- No trailing commas needed in JSX but are safe to include

### Valid Planet Names (case-sensitive, exactly as shown):
`"Sun"` `"Moon"` `"Mars"` `"Mercury"` `"Jupiter"` `"Venus"` `"Saturn"` `"Rahu"` `"Ketu"`

---

## 14. Session Log

Use this section to record what was done in each agent session.

| Date | Agent | Files Processed | Notes |
|---|---|---|---|
| 2026-07-28 | Kilo | 1 blog file | Processed 100112_1st_Lord_in_1nd_House.mdx (1st Lord in 12th House): Embedded KundaliChart, updated SEO frontmatter, replaced FAQ with FAQBlock, updated Related Articles. |
| 2026-07-28 | Composer | BATCH 1 complete + BATCH 2 HIGH/MED | BATCH 1: finished 100800, 100202; fixed /blogs-md/ links on 100802 + 100208. BATCH 2: processed Sun in 1st (`060101` filename quirk), 2nd, 4th, 5th — KundaliChart + FAQBlock + `/blogs/[category]/[slug]` links + modifiedDate. Note: `060101_Sun_in_11th_House.mdx` = Sun in 1st content; `060112` = Sun in 12th. Remaining BATCH 2 LOW + BATCH 3 next. |
| 2026-07-28 | Composer | BATCH 2 complete (all Sun houses) | Processed remaining LOW Sun files: 3rd, 6th, 7th, 8th, 9th, 10th, 11th, 12th (`060112`). BATCH 2 fully done. Next: BATCH 3 Moon in Houses. |
| 2026-07-28 | Composer | VALIDATION GATE passed | BATCH 1+2: 17/17 MDX checklist pass. Main app: path-resolver + kundali-chart-math + content-processor green (22 tests). Fixed leftover Prev/Next .mdx links. Cleared for BATCH 3 Moon. |
| 2026-07-28 | Composer | BATCH 3 complete (Moon in Houses) | Processed all 12 Moon-in-house articles (060201=1st/Cancer lagna; 060212=12th). Fixed corrupted 4th/5th frontmatter. Validated 12/12 checklist before commit. |
| | | | |

---


---

## 15. CURRENT STATUS HANDOVER (2026-07-28) — READ THIS FIRST FOR CONTINUATION

### Mission (unchanged)
Enhance MDX blogs in `06_Planet_in_Houses/` and `10_Lord_in_Houses/` by embedding interactive `<KundaliChart />`, `<FAQBlock />`, SEO frontmatter (`modifiedDate: '2026-07-28'`), and standardized internal links. Spec + API + workflow live in sections 1–14 of this file.

### Repositories
| Repo | Path | Branch | Role |
|---|---|---|---|
| **Content** | `/Users/bishalghimire/Documents/WORK/Open Source/astro-blogs` | `dev` | All `.mdx` blog content |
| **Main app** | `/Users/bishalghimire/Documents/WORK/Code/AstroFusion/astrofusion-nextjs` | `dev` | MDX component registry + path resolver |

### Completed batches (validated + committed)
| Batch | Scope | Status | Content commit(s) |
|---|---|---|---|
| **BATCH 1** | GSC-priority Lord-in-Houses (5 files) | ✅ Done + validated | `7bd1699`, link fix `92db15b` |
| **BATCH 2** | All Sun in Houses (12 files) | ✅ Done + validated | `9501770` |
| **BATCH 3** | All Moon in Houses (12 files) | ✅ Done + validated | `2a09eb5` |
| Validation gate | BATCH 1–2 checklist 17/17; Moon 12/12 | ✅ Passed before BATCH 3 | `c741c8a`, `92db15b` |

**Main-app supporting commit:** `3e03b7e67d` — short-link suffix matching in `findCanonicalPath` + Kundali chart lagna label fix + unit tests.

### Per-file quality checklist (MUST pass before marking done)
- [ ] `<KundaliChart />` with correct planet/house/`lagnaRashi`
- [ ] `highlightHouses` matches discussed houses
- [ ] `effects` derived from article (3–4 bullets)
- [ ] Frontmatter title contains primary keyword; description ~150–160 chars
- [ ] `modifiedDate: '2026-07-28'`
- [ ] `<FAQBlock faqs={[...]} />` with **4+** Q&As
- [ ] `## Related Articles` with **3+** `/blogs/...` links (no `.md`/`.mdx`, never `/blogs-md/`)
- [ ] Do not remove body content; only add/improve

### Internal link standard (CRITICAL)
Format: `/blogs/[category]/[slug]` — **no** `.md`/`.mdx`, **no** `/blogs-md/`.

Examples that work (app path-resolver suffix-matches nested paths):
- `/blogs/1008_8th_Lord_in_all_Houses/100802_8th_Lord_in_2nd_House`
- `/blogs/0601_Sun_in_Houses/060102_Sun_in_2nd_House`
- `/blogs/0602_Moon_in_Houses/060204_Moon_in_4th_House`
- `/blogs/02_Houses/202_2nd_House_in_Vedic_Astrology`
- `/blogs/03_Planets/0301_Sun`

Main app now resolves short category paths even when canonical path includes parent folder (`10_Lord_in_Houses/...`, `06_Planet_in_Houses/...`) via suffix/segment-tail match in:
`packages/services/content/src/blogs/utils/path-resolver.ts`

### KundaliChart rules (quick reference)
**Planet-in-House (default):** `lagnaRashi={1}` (Aries), `placements={[{ planet, house }]}`, `highlightHouses={[house]}`.

**Planet in 1st House (special):**
| Planet | lagnaRashi | Reason |
|---|---|---|
| Sun | 5 (Leo) | Sun rules Leo |
| Moon | 4 (Cancer) | Moon rules Cancer |
| Mars | 1 | Mars rules Aries |
| Mercury | 3 | Gemini |
| Jupiter | 9 | Sagittarius |
| Venus | 2 | Taurus |
| Saturn | 10 | Capricorn |
| Rahu/Ketu | 1 | Generic Aries |

**Lord-in-House (Aries lagna default):** use lord→planet table in §4. Example: 8th lord = Mars in house M with `isLordOf: 8`, `highlightHouses={[8, M]}`.

**Component aliases** (registered in main app `custom-components.tsx`): `KundaliChart`, `KundaliIllustration`, `BlogInteractiveKundaliChart` — no import needed in MDX.

### CRITICAL filename quirks (content ≠ filename)
**Always trust H1/title content over filename.**

Sun (`0601_Sun_in_Houses/`):
- `060101_Sun_in_11th_House.mdx` → **Sun in 1st** (use lagnaRashi=5)
- `060111_Sun_in_11th_House.mdx` → Sun in 11th
- `060112_Sun_in_1nd_House.mdx` → **Sun in 12th**

Moon (`0602_Moon_in_Houses/`):
- `060201_Moon_in_11th_House.mdx` → **Moon in 1st** (use lagnaRashi=4)
- `060211_Moon_in_11th_House.mdx` → Moon in 11th
- `060212_Moon_in_1nd_House.mdx` → **Moon in 12th**

Lords (same pattern across folders):
- `*01_*_11th_House.mdx` often = **1st house** content
- `*12_*_1nd_House.mdx` often = **12th house** content
- Example: `100801_8th_Lord_in_11th_House.mdx` = 8th lord in **1st**; `100812_8th_Lord_in_1nd_House.mdx` = 8th lord in **12th**
- When linking, use the **actual filename** that exists on disk

### What BATCH 4 must do next
1. Process remaining `10_Lord_in_Houses/` folder-by-folder (see BATCH 4 checklist above).
2. **Already done inside those folders** (do not redo / do not regress):
   - `100802`, `100800` (8th lord)
   - `100208`, `100202` (2nd lord)
   - `100112` (1st lord in 12th — filename `1nd`)
3. For each remaining file: embed chart, FAQBlock, modifiedDate, fix links, Related Articles.
4. Parivartana pairs (§9): when editing both sides of an exchange, add dual-planet chart + cross-links + `<InfoBlock>`.
5. **Validate each folder** (or batch) before committing: checklist above + no `/blogs-md/` + no `.mdx` in links.
6. **Commit after each folder/milestone** on `dev` (user requested milestone commits).
7. Then BATCH 5 (Mars→Ketu planet-in-houses).

### Suggested validation one-liner (content repo)
Check each processed file for: `KundaliChart`, `FAQBlock`, `modifiedDate: '2026-07-28'`, zero `/blogs-md/`, zero `](...mdx)` links, `lagnaRashi`/`house` match content.

### Main-app tests (relevant)
```bash
cd /Users/bishalghimire/Documents/WORK/Code/AstroFusion/astrofusion-nextjs
pnpm exec vitest run packages/services/content/src/blogs/utils/__tests__/path-resolver.test.ts \
  apps/web/astro-fusion/src/app/[locale]/blogs/components/mdx/__tests__/kundali-chart-math.test.ts
cd apps/web/astro-fusion && pnpm exec vitest run "src/app/[locale]/blogs/__tests__/content-processor.test.ts"
```
Note: older `apps/web/astro-fusion/src/tests/lib/blogs/*` suites use **local outdated mock copies** of path helpers and fail; ignore unless rewriting them to import `@astrofusion/services-content`.

### DO NOT TOUCH (other agents / unrelated dirty files in content repo)
Leave alone unless explicitly asked:
- Uncommitted edits under `02_Houses/201–208`, `05_Nakshatra/0501–0502`
- `blog-index-*.json`, `raw-index-structure.json`
- Untracked `rename.sh`, `rename_all.sh`, `rename_files.py`, `temp_categories/`

### Git rules for agents
- Work on `dev` only; no stash; no hard reset; no force push
- Commit only your files; milestone commits after each completed batch/folder
- Content changes → `astro-blogs`; component/resolver changes → `astrofusion-nextjs`

### Insertion point reminder
`<KundaliChart />` AFTER opening `<AIBlufSummary>` (or first intro paragraph), BEFORE first major `##` body section. FAQBlock near end before Related Articles.


*Last updated: 2026-07-28 by Composer (status §15 written for agent continuation)*
*Source of truth for: `astro-fusion/astro-blogs` Kundali Chart Embedding Project*
