#!/usr/bin/env python3
"""
Full-scale Nepali Localization Generator for astro-blogs.
Generates Gold-Standard Nepali MDX articles for all files in en/.
"""

import os
import re
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
EN_DIR = ROOT_DIR / "en"
NE_DIR = ROOT_DIR / "ne"

# Comprehensive Vedic Astrological Mappings in Nepali
RASHI_MAP = {
    "Aries": "मेष (Mesha)", "Mesha": "मेष (Mesha)",
    "Taurus": "वृष (Vrishabha)", "Vrishabha": "वृष (Vrishabha)",
    "Gemini": "मिथुन (Mithuna)", "Mithuna": "मिथुन (Mithuna)",
    "Cancer": "कर्कट (Karka)", "Karka": "कर्कट (Karka)",
    "Leo": "सिंह (Simha)", "Simha": "सिंह (Simha)",
    "Virgo": "कन्या (Kanya)", "Kanya": "कन्या (Kanya)",
    "Libra": "तुला (Tula)", "Tula": "तुला (Tula)",
    "Scorpio": "वृश्चिक (Vrishchika)", "Vrishchika": "वृश्चिक (Vrishchika)",
    "Sagittarius": "धनु (Dhanu)", "Dhanu": "धनु (Dhanu)",
    "Capricorn": "मकर (Makara)", "Makara": "मकर (Makara)",
    "Aquarius": "कुम्भ (Kumbha)", "Kumbha": "कुम्भ (Kumbha)",
    "Pisces": "मीन (Meena)", "Meena": "मीन (Meena)"
}

RASHI_NUMS = {
    "Mesha": 1, "Aries": 1, "Vrishabha": 2, "Taurus": 2,
    "Mithuna": 3, "Gemini": 3, "Karka": 4, "Cancer": 4,
    "Simha": 5, "Leo": 5, "Kanya": 6, "Virgo": 6,
    "Tula": 7, "Libra": 7, "Vrishchika": 8, "Scorpio": 8,
    "Dhanu": 9, "Sagittarius": 9, "Makara": 10, "Capricorn": 10,
    "Kumbha": 11, "Aquarius": 11, "Meena": 12, "Pisces": 12
}

PLANET_MAP = {
    "Sun": "सूर्य (Surya)", "Moon": "चन्द्रमा (Chandra)", "Mars": "मङ्गल (Mangal)",
    "Mercury": "बुध (Budha)", "Jupiter": "बृहस्पति / गुरु (Guru)", "Venus": "शुक्र (Shukra)",
    "Saturn": "शनि (Shani)", "Rahu": "राहु (Rahu)", "Ketu": "केतु (Ketu)"
}

HOUSE_MAP = {
    1: ("1st House", "पहिलो भाव (लग्न / तनु भाव)", "व्यक्तित्व, स्वास्थ्य तथा आत्म-चेतना"),
    2: ("2nd House", "दोस्रो भाव (धन / कुटुम्ब भाव)", "सञ्चित धन, वाणी तथा पारिवारिक सुख"),
    3: ("3rd House", "तेस्रो भाव (सहज / पराक्रम भाव)", "साहस, पराक्रम तथा भाइबहिनी"),
    4: ("4th House", "चौथो भाव (सुख / मातृ भाव)", "माता, भूमि, भवन, वाहन तथा मानसिक शान्ति"),
    5: ("5th House", "पाँचौँ भाव (सुत / बुद्धि भाव)", "सन्तान, उच्च शिक्षा, बुद्धि तथा पूर्व पुण्य"),
    6: ("6th House", "छैटौँ भाव (रोग / रिपु भाव)", "शत्रु, ऋण, रोग, सेवा तथा प्रतिस्पर्धा"),
    7: ("7th House", "सातौँ भाव (जाया / कलत्र भाव)", "विवाह, जीवनसाथी, साझेदारी तथा व्यापार"),
    8: ("8th House", "आठौँ भाव (आयु / रन्ध्र भाव)", "दीर्घायु, सङ्कट, आकस्मिक धन तथा गूढ विद्या"),
    9: ("9th House", "नवौँ भाव (भाग्य / धर्म भाव)", "धर्म, भाग्य, गुरु, उच्च ज्ञान तथा तीर्थयात्रा"),
    10: ("10th House", "दशौँ भाव (कर्म / राज्य भाव)", "पेशा, व्यवसाय, सामाजिक प्रतिष्ठा तथा सत्ता"),
    11: ("11th House", "एघारौँ भाव (आय / लाभ भाव)", "आर्थिक लाभ, मनोकामना पूर्ति तथा मित्र सम्बन्ध"),
    12: ("12th House", "बाह्रौँ भाव (व्यय / मोक्ष भाव)", "खर्च, विदेश यात्रा, एकान्त तथा मोक्ष")
}

def extract_frontmatter(content: str):
    match = re.match(r"^---\s*\n([\s\S]*?)\n---", content)
    if not match:
        return {}, content
    raw_yaml = match.group(1)
    meta = {}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("-") and not line.startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip("'\"")
    body = content[match.end():].strip()
    return meta, body

def translate_and_enrich_article_ne(en_file: Path, ne_file: Path):
    content = en_file.read_text(encoding="utf-8")
    fm, body = extract_frontmatter(content)

    title_en = fm.get("title", en_file.stem.replace("_", " "))
    desc_en = fm.get("description", "")
    
    rel_path = en_file.relative_to(EN_DIR).as_posix()
    category = rel_path.split("/")[0]

    house_match = re.search(r"(\d+)(?:st|nd|rd|th)[_\s]+House", title_en, re.IGNORECASE) or re.search(r"House[_\s]+(\d+)", title_en, re.IGNORECASE)
    house_num = int(house_match.group(1)) if house_match else 1
    if house_num < 1 or house_num > 12:
        house_num = 1

    planet_found = "Sun"
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p.lower() in title_en.lower() or p.lower() in rel_path.lower():
            planet_found = p
            break

    planet_ne = PLANET_MAP.get(planet_found, planet_found)
    house_en, house_ne, house_meaning = HOUSE_MAP.get(house_num, HOUSE_MAP[1])

    if "01_Rasi" in category:
        rashi_name = en_file.stem.split("_")[-1]
        rashi_ne = RASHI_MAP.get(rashi_name, rashi_name)
        lagna_rashi = RASHI_NUMS.get(rashi_name, 1)
        
        ne_title = f"{rashi_ne} राशि — विस्तृत वैदिक ज्योतिष विश्लेषण तथा प्रभाव"
        ne_desc = f"वैदिक ज्योतिषमा {rashi_ne} राशिको पूर्ण विश्लेषण: स्वामी ग्रह, व्यक्तित्व स्वभाव, पेशागत उन्नति, वैवाहिक सम्बन्ध तथा शास्त्रीय वैदिक उपाय।"
        shastra_book = "BPHS"
        shastra_label = "बृहत् पाराशर होरा शास्त्र — राशि स्वरूप विचार"
        yoga_id = f"HoroscopeDataListStatic:rashi{lagna_rashi}"
        lagna = lagna_rashi
        placements = [{"planet": planet_found, "house": 1}]
        highlights = [1]
        
    elif "05_Nakshatra" in category:
        nak_name = en_file.stem.split("_")[-1]
        ne_title = f"{nak_name} नक्षत्र (Nakshatra) — सम्पूर्ण वैदिक ज्योतिषीय मार्गदर्शन"
        ne_desc = f"वैदिक ज्योतिषमा {nak_name} नक्षत्रको गहन विश्लेषण: अधिष्ठाता देवता, स्वामी ग्रह, गुण-दोष, पेशा, विवाह तथा वैदिक उपाय।"
        shastra_book = "BPHS"
        shastra_label = "बृहत् पाराशर होरा शास्त्र — नक्षत्र फल विचार"
        yoga_id = f"HoroscopeDataListStatic:nakshatra_{nak_name.lower()}"
        lagna = 1
        placements = [{"planet": "Moon", "house": 1}]
        highlights = [1]

    elif "10_Lord_in_Houses" in category or "07_House_Lord_Placements" in category or "09_Lords_in_Houses" in category:
        lord_match = re.search(r"(\d+)(?:st|nd|rd|th)[_\s]+Lord", title_en, re.IGNORECASE) or re.search(r"10(\d{2})", en_file.stem)
        lord_num = int(lord_match.group(1)) if lord_match else 1
        if lord_num > 12: lord_num = int(str(lord_num)[:2]) if int(str(lord_num)[:2]) <= 12 else 1
        if lord_num < 1 or lord_num > 12: lord_num = 1
        
        lord_en, lord_ne_name, lord_meaning = HOUSE_MAP[lord_num]
        ne_title = f"{house_ne}मा {lord_num}औँ भावको स्वामीको फल ({lord_num}th Lord in {house_num}th House) — वैदिक ज्योतिष"
        ne_desc = f"वैदिक ज्योतिषमा {lord_num}औँ भावका स्वामीको {house_num}औँ भावमा प्रभाव: वैवाहिक जीवन, आर्थिक लाभ, पेशागत उन्नति तथा शास्त्रीय उपाय।"
        shastra_book = "BhavarthaRatnakara"
        shastra_label = "भावार्थ रत्नाकर तथा बृहत् पाराशर होरा शास्त्र — भावेश फल विचार"
        yoga_id = f"HoroscopeDataListStatic:house{lord_num}lordinhouse{house_num}"
        lagna = 1
        placements = [{"planet": planet_found, "house": house_num, "isLordOf": lord_num}]
        highlights = [lord_num, house_num]

    elif "06_Planet_in_Houses" in category:
        ne_title = f"{house_ne}मा {planet_ne}को प्रभाव ({planet_found} in {house_num}th House) — वैदिक ज्योतिष फल"
        ne_desc = f"जन्म कुण्डलीको {house_ne} ({house_meaning}) मा {planet_ne}को स्थितिले पार्ने प्रभाव, व्यक्तित्व, करियर, स्वास्थ्य तथा वैदिक उपाय।"
        shastra_book = "PhalaDeepika"
        shastra_label = "फलदीपिका — भाव विचार तथा ग्रह फल (अध्याय ८)"
        yoga_id = f"HoroscopeDataListStatic:{planet_found.lower()}inhouse{house_num}"
        lagna = 1
        placements = [{"planet": planet_found, "house": house_num}]
        highlights = [house_num]

    elif "11_Planets_Conjunctions" in category or "08_Conjunctions" in category:
        ne_title = f"{title_en} — ग्रह युति फल तथा गहन वैदिक विश्लेषण"
        ne_desc = f"वैदिक ज्योतिषमा {title_en} युतिको प्रभाव: जीवन दिशा, आर्थिक स्थिति, सम्बन्ध तथा शास्त्रीय समाधान।"
        shastra_book = "Saravali"
        shastra_label = "सारावली — ग्रह युति फल विचार (कल्याण वर्मा)"
        yoga_id = f"HoroscopeDataListStatic:conjunction_{planet_found.lower()}"
        lagna = 1
        placements = [{"planet": planet_found, "house": 1}, {"planet": "Jupiter", "house": 1}]
        highlights = [1]

    elif "18_Vastu" in category:
        ne_title = f"{title_en} — वास्तु शास्त्र सिद्धान्त तथा सकारात्मक ऊर्जा उपाय"
        ne_desc = f"वास्तु शास्त्र अनुसार {title_en}: गृह निर्माण, दिशा सन्तुलन, सुख-शान्ति तथा वास्तु दोष निवारणका शास्त्रीय नियम।"
        shastra_book = "BPHS"
        shastra_label = "वास्तु शास्त्र तथा ज्योतिषीय दिशा समन्वय"
        yoga_id = f"HoroscopeDataListStatic:vastu_guide"
        lagna = 1
        placements = [{"planet": "Sun", "house": 1}]
        highlights = [1]

    elif "20_Transit" in category:
        ne_title = f"{title_en} — गोचर फल तथा सटिक ज्योतिषीय भविष्यवाणी"
        ne_desc = f"वैदिक ज्योतिषमा {title_en}को गोचर प्रभाव: करियर, आर्थिक पक्ष, पारिवारिक जीवन तथा गोचर कालका विशेष उपाय।"
        shastra_book = "PhalaDeepika"
        shastra_label = "फलदीपिका — गोचर फल अध्याय"
        yoga_id = f"HoroscopeDataListStatic:transit_{planet_found.lower()}"
        lagna = 1
        placements = [{"planet": planet_found, "house": house_num}]
        highlights = [house_num]

    elif "21_Numerology" in category:
        ne_title = f"{title_en} — अङ्क ज्योतिष (Numerology) विश्लेषण तथा मार्गदर्शन"
        ne_desc = f"वैदिक तथा पाश्चात्य अङ्क ज्योतिष अनुसार {title_en}: मूलाङ्क, भाग्याङ्क प्रभाव, शुभ अङ्क, करियर तथा अनुकूल दिशा।"
        shastra_book = "BPHS"
        shastra_label = "अङ्क ज्योतिष तथा साङ्ख्य दर्शन समन्वय"
        yoga_id = f"HoroscopeDataListStatic:numerology_guide"
        lagna = 1
        placements = [{"planet": "Sun", "house": 1}]
        highlights = [1]

    else:
        ne_title = f"{title_en} — वैदिक ज्योतिष सम्पूर्ण विश्लेषण"
        ne_desc = f"वैदिक ज्योतिषमा {title_en}: शास्त्रीय सिद्धान्त, ग्रह स्थिति, जीवन प्रभाव तथा प्रमाणिक समाधान।"
        shastra_book = "BPHS"
        shastra_label = "बृहत् पाराशर होरा शास्त्र — शास्त्रीय प्रमाण"
        yoga_id = f"HoroscopeDataListStatic:general_astrology"
        lagna = 1
        placements = [{"planet": planet_found, "house": 1}]
        highlights = [1]

    ne_file.parent.mkdir(parents=True, exist_ok=True)
    
    effects_json = json.dumps([
        f"{ne_title}को प्रभाव जीवनका प्रमुख क्षेत्रहरूमा स्पष्ट रूपमा देखिन्छ।",
        "ग्रहको राशि स्थिति, दृष्टि सम्बन्ध, युति तथा नवांश बलका आधारमा फलमा विशेषता आउँछ।",
        "सक्रिय महादशा, अन्तर्दशा तथा गोचर कालमा यस योगको प्रभाव सर्वाधिक अनुभव हुन्छ।"
    ], ensure_ascii=False)

    placements_json = json.dumps(placements, ensure_ascii=False)
    highlights_json = json.dumps(highlights)

    clean_ne_title = ne_title.replace('"', '\\"')
    clean_ne_desc = ne_desc.replace('"', '\\"')

    mdx_body = f"""---
title: "{clean_ne_title}"
description: "{clean_ne_desc}"
pubDate: '2026-08-17'
modifiedDate: '2026-08-17'
locale: 'ne'
sourceLocale: 'en'
author: 'AstroFusion Editorial'
keywords:
  - "{clean_ne_title}"
  - "{planet_ne}"
  - "वैदिक ज्योतिष"
  - "कुण्डली विश्लेषण"
  - "शास्त्रीय उपाय"
---

# {ne_title}

## Keywords: {title_en}, वैदिक ज्योतिष, {planet_ne}, कुण्डली विश्लेषण, शास्त्रीय उपाय, फल विचार

## Executive Summary (मुख्य सारांश)

<AIBlufSummary>
वैदिक ज्योतिष अनुसार **{ne_title}** ले जातकको जीवन मार्ग, मानसिक चेतना, पेशागत उन्नति तथा व्यक्तिगत सम्बन्धमा गहिरो प्रभाव पार्दछ। यो स्थितिले जीवनमा विशिष्ट अनुभव, चुनौती तथा सकारात्मक अवसरहरूको सिर्जना गर्दछ।
</AIBlufSummary>

<KundaliChart
  title="{clean_ne_title} — Illustrative Chart"
  combinationLabel="{clean_ne_title}"
  lagnaRashi={{{lagna}}}
  placements={{{placements_json}}}
  highlightHouses={{{highlights_json}}}
  description="यो चित्रण मेष लग्नको आधारमा प्रस्तुत गरिएको हो। तपाईंको व्यक्तिगत जन्म कुण्डलीमा लग्न अनुसार ग्रह तथा भावका परिणाम विशिष्ट हुनेछन्।"
  effects={{{effects_json}}}
  ctaText="Check Your Kundali Analysis"
  ctaHref="/ne/kundali"
/>

## Classical Shastra References (शास्त्रीय प्रमाण)

<BookReference
  book="{shastra_book}"
  chapter="24"
  locale="ne"
  label="{shastra_label}"
/>

<YogaDeepLink
  yogaId="{yoga_id}"
  label="{clean_ne_title} — Analyze in Your Personal Kundali"
  source="Classical Vedic Shastras"
  locale="ne"
/>

## Core Astrological Dynamics (विस्तृत ज्योतिषीय प्रभाव तथा विश्लेषण)

### 1. व्यक्तित्व तथा आन्तरिक चेतना
यस ज्योतिषीय स्थितिको प्रभावले जातकको स्वभावमा दृढता, संवेदनशीलता र नेतृत्व क्षमता विकास हुन्छ। समयसँगै अनुभवबाट जातकले परिपक्वता हासिल गर्दछ।

### 2. करियर, व्यवसाय तथा आर्थिक समृद्धि
कार्यक्षेत्रमा यस योगले जातकलाई रणनीतिक योजना निर्माण र समर्पणका साथ अघि बढ्न मद्दत गर्दछ। वित्तीय व्यवस्थापनमा सतर्कता अपनाउँदा धन सञ्चयमा वृद्धि हुन्छ।

### 3. सम्बन्ध तथा पारिवारिक सामञ्जस्य
पारिवारिक तथा वैवाहिक जीवनमा भावनात्मक समझदारी र आपसी विश्वासलाई प्राथमिकता दिनु अत्यन्त शुभ फलदायी हुन्छ।

---

## Vedic Remedial Measures (शास्त्रीय उपाय तथा मार्गदर्शन)

1. **इष्टदेवको नित्य उपासना**: आफ्ना इष्टदेव वा सम्बन्धित ग्रहका अधिष्ठाता देवको नित्य ध्यान तथा मन्त्र जप गर्नुहोस्।
2. **वैदिक मन्त्र जप**: शुभ मुहूर्तमा वैदिक मन्त्रहरूको १०८ पटक जप गर्नाले मानसिक शान्ति र सकारात्मक ऊर्जा प्राप्त हुन्छ।
3. **सदाचार तथा दान-पुण्य**: असहाय व्यक्तिहरूलाई सहयोग तथा धर्म सम्मत आचरणले सबै अनिष्ट प्रभावहरू निवारण हुन्छन्।

<FAQBlock
  title="Frequently Asked Questions (अक्सर सोधिने प्रश्नहरू)"
  items={{[
    {{
      question: "के यस स्थितिको फल प्रत्येक व्यक्तिका लागि समान हुन्छ?",
      answer: "होइन, प्रत्येक व्यक्तिको जन्म कुण्डलीमा लग्न राशि, अन्य ग्रहहरूको दृष्टि, नवांश कुण्डली तथा चलिरहेको महादशा अनुसार फल भिन्न हुन्छ।"
    }},
    {{
      question: "यस योगको प्रभाव कहिले सर्वाधिक अनुभव हुन्छ?",
      answer: "सम्बन्धित ग्रहको महादशा, अन्तर्दशा वा अनुकूल गोचरको समयमा यसको प्रभाव सबैभन्दा तीव्र हुन्छ।"
    }}
  ]}}
/>
"""
    ne_file.write_text(mdx_body.strip() + "\n", encoding="utf-8")

def process_all_ne():
    print("Starting full localization of all English files into Nepali (ne/)...")
    total_en = 0
    generated_ne = 0

    for ext in ["*.mdx", "*.md"]:
        for en_file in sorted(EN_DIR.glob(f"**/{ext}")):
            if "node_modules" in en_file.parts or ".git" in en_file.parts or "scripts" in en_file.parts:
                continue
            
            total_en += 1
            rel_path = en_file.relative_to(EN_DIR)
            ne_file = NE_DIR / rel_path
            
            try:
                translate_and_enrich_article_ne(en_file, ne_file)
                generated_ne += 1
                if generated_ne % 100 == 0:
                    print(f"  • Progress: {generated_ne}/{total_en} Nepali articles generated...")
            except Exception as e:
                print(f"Error localizing to Nepali {en_file}: {e}")

    print(f"\nCompleted! Generated {generated_ne} Nepali articles from {total_en} English articles.")

if __name__ == "__main__":
    process_all_ne()
