#!/usr/bin/env python3
"""
Generate P0 Hindi Blog Articles for High-Intent House Lord Placements & Planets in Houses
Includes:
- Standardized Vedic terminology (Lords, Bhavas, Yogas)
- Interactive <KundaliChart /> in Hindi
- <YogaDeepLink /> to Kundali Yoga Analysis report
- <BookReference /> with classical Sanskrit citations (BPHS, Bhavartha Ratnakara, PhalaDeepika)
- Enriched YAML frontmatter for Hindi SERP ranking
- Exact Gold Standard template compliance
"""

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
HI_DIR = ROOT_DIR / "hi"

HOUSE_NAMES = {
    1: ("1st", "प्रथम", "लग्न / तनु भाव (व्यक्तित्व, स्वास्थ्य)"),
    2: ("2nd", "द्वितीय", "धन / कुटुंब भाव (संचित धन, वाणी, परिवार)"),
    3: ("3rd", "तृतीय", "सहज / पराक्रम भाव (साहस, छोटे भाई-बहन)"),
    4: ("4th", "चतुर्थ", "सुख / मातृ भाव (माता, भूमि, वाहन, मानसिक शांति)"),
    5: ("5th", "पंचम", "सुत / बुद्धि भाव (संतान, उच्च विद्या, पूर्व पुण्य)"),
    6: ("6th", "षष्ठ", "रोग / रिपु भाव (शत्रु, ऋण, रोग, दैनिक सेवा)"),
    7: ("7th", "सप्तम", "कलत्र / जाया भाव (विवाह, जीवनसाथी, साझेदारी, व्यापार)"),
    8: ("8th", "अष्टम", "आयु / रन्ध्र भाव (आयु, संकट, आकस्मिक धन, गूढ़ विद्या)"),
    9: ("9th", "नवम", "धर्म / भाग्य भाव (भाग्य, धर्म, गुरु, तीर्थयात्रा)"),
    10: ("10th", "दशम", "कर्म / राज्य भाव (व्यवसाय, प्रतिष्ठा, सत्ता)"),
    11: ("11th", "एकादश", "आय / लाभ भाव (आर्थिक लाभ, बड़े भाई, महत्वाकांक्षा)"),
    12: ("12th", "द्वादश", "व्यय / मोक्ष भाव (व्यय, विदेश यात्रा, मोक्ष, अस्पताल)"),
}

LORD_NAMES = {
    1: ("1st Lord", "लग्नेश", "Mars", 1),
    2: ("2nd Lord", "द्वितीयेश (धनेश)", "Venus", 2),
    3: ("3rd Lord", "तृतीयेश (सहजेश)", "Mercury", 3),
    4: ("4th Lord", "चतुर्थेश (सुखेश)", "Moon", 4),
    5: ("5th Lord", "पंचमेश (पुत्रेश)", "Sun", 5),
    6: ("6th Lord", "षष्ठेश (रोगेश)", "Mercury", 6),
    7: ("7th Lord", "सप्तमेश (कलत्रेश)", "Venus", 7),
    8: ("8th Lord", "अष्टमेश", "Mars", 8),
    9: ("9th Lord", "नवमेश (भाग्येश)", "Jupiter", 9),
    10: ("10th Lord", "दशमेश (कर्मेश)", "Saturn", 10),
    11: ("11th Lord", "एकादशेश (लाभेश)", "Saturn", 11),
    12: ("12th Lord", "द्वादशेश (व्ययेश)", "Jupiter", 12),
}

def generate_lord_article(lord_num: int, place_num: int):
    lord_en, lord_hi, rep_planet, rep_sign = LORD_NAMES[lord_num]
    place_en, place_hi, place_desc = HOUSE_NAMES[place_num]
    lord_desc = HOUSE_NAMES[lord_num][2]

    folder_name = f"10{lord_num:02d}_{lord_en.split()[0]}_Lord_in_all_Houses"
    file_name = f"10{lord_num:02d}{place_num:02d}_{lord_en.split()[0]}_Lord_in_{place_en.split()[0]}_House.mdx"

    target_dir = HI_DIR / "10_Lord_in_Houses" / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / file_name

    content = f"""---
title: "{lord_en} in {place_en} House ({place_hi} भाव में {lord_hi}) — Vedic Astrology Analysis"
description: "Comprehensive Vedic astrology analysis of {lord_en} in {place_en} House ({place_hi} भाव में {lord_hi}): {lord_desc}, {place_desc}, marriage, wealth, and classical remedies."
pubDate: '2026-08-17'
modifiedDate: '2026-08-17'
locale: 'hi'
sourceLocale: 'en'
author: 'AstroFusion Editorial'
keywords:
  - "{lord_hi} {place_hi} भाव में"
  - "{place_hi} भाव में {lord_hi}"
  - "{lord_en.lower()} in {place_en.lower()} house"
  - "ruler of {lord_num}th house in {place_num}th house"
  - "Vedic astrology {place_en.lower()} house"
  - "बृहत् पाराशर होरा शास्त्र"
  - "भावार्थ रत्नाकर"
---

# {place_hi} भाव में {lord_hi}: गहन वैदिक ज्योतिषीय विश्लेषण ({lord_en} in {place_en} House)

## Keywords: {lord_en} in {place_en} House, {place_hi} भाव में {lord_hi}, वैदिक ज्योतिष, {lord_desc}, {place_desc}, शास्त्रीय उपाय

## Executive Summary (मुख्य सारांश)

<AIBlufSummary>
वैदिक ज्योतिष के अनुसार जब **{lord_hi}** ({lord_desc}) कुण्डली के **{place_hi} भाव** ({place_desc}) में विराजमान होते हैं, तो यह दोनों भावों के मध्य एक गहन कार्मिक संबंध स्थापित करता है। यह स्थिति जातक के जीवन में महत्वपूर्ण परिवर्तन, सीखने के अनुभव तथा विशिष्ट परिणाम प्रदान करती है।
</AIBlufSummary>

<KundaliChart
  title="{place_hi} भाव में {lord_hi} — Illustrative Chart"
  combinationLabel="{place_hi} भाव में {lord_hi} ({lord_en} in {place_en} House)"
  lagnaRashi={{1}}
  placements={{[{{ planet: "{rep_planet}", house: {place_num}, isLordOf: {lord_num} }}]}}
  highlightHouses={{[{lord_num}, {place_num}]}}
  description="यह चित्रण मेष लग्न की कुण्डली के आधार पर {lord_hi} ({rep_planet}) की {place_hi} भाव में स्थिति को दर्शाता है। आपकी व्यक्तिगत कुण्डली में लग्न के अनुसार ग्रह एवं भाव के स्वामी भिन्न होंगे।"
  effects={{[
    "{lord_hi} का प्रभाव {place_hi} भाव के मुख्य क्षेत्रों पर पड़ता है।",
    "ग्रह की उच्चता, नीचता, मित्र/शत्रु राशि तथा दृष्टि से फलों में परिवर्तन होता है।",
    "दशा और अंतर्दशा काल में यह स्थिति सर्वाधिक सक्रिय और फलदायी होती है।"
  ]}}
  ctaText="Check Your {lord_en} Placement"
  ctaHref="/hi/kundali"
/>

## Classical Shastra References (शास्त्रीय प्रमाण)

<BookReference
  book="BPHS"
  chapter="24"
  locale="hi"
  label="Brihat Parashara Hora Shastra — Chapter 24 (Bhavesha Phala)"
/>

<YogaDeepLink
  yogaId="HoroscopeDataListStatic:house{lord_num}lordinhouse{place_num}"
  label="{place_hi} भाव में {lord_hi} — Analyze in Your Personal Kundali"
  source="Bhavartha Ratnakara & Parashara"
  locale="hi"
/>

## Core Astrological Dynamics (मुख्य प्रभाव एवं फल)

### 1. सामान्य एवं कार्मिक प्रभाव
जब {lord_num}वें भाव के अधिपति {place_num}वें भाव में बैठते हैं, तो जातक के जीवन में {lord_desc} से जुड़े विषय {place_desc} के माध्यम से व्यक्त होते हैं। यदि ग्रह शुभ भाव में और बलवान हो, तो शुभ परिणाम प्राप्त होते हैं, जबकि पाप प्रभाव में होने पर संघर्ष उत्पन्न हो सकता है।

### 2. आर्थिक एवं पारिवारिक प्रभाव
धन और परिवार के संदर्भ में, यह स्थिति जातक को अपने उत्तरदायित्वों को नए दृष्टिकोण से समझने की प्रेरणा देती है। साझेदारी, पारिवारिक सहयोग तथा आकस्मिक आर्थिक बदलावों का विशेष प्रभाव देखने को मिलता है।

### 3. करियर एवं सामाजिक प्रतिष्ठा
कार्यक्षेत्र में यह योग जातक को गहरी विश्लेषणात्मक क्षमता और नेतृत्व कौशल प्रदान कर सकता है। समय के साथ अनुभव और धैर्य से कार्यों में सफलता मिलती है।

---

## Vedic Remedial Measures (शास्त्रीय उपाय)

1. **इष्टदेव उपासना**: संबंधित भावेश के अधिष्ठाता देवता की नित्य उपासना और स्तोत्र पाठ करें।
2. **वैदिक मंत्र जप**: संबंधित ग्रह के वैदिक मंत्रों का जप तथा दान-पुण्य से अनिष्ट प्रभावों को शांत किया जा सकता है।
3. **पारदर्शिता एवं सदाचार**: व्यक्तिगत तथा व्यावसायिक जीवन में सत्य और पारदर्शिता बनाए रखें।

<FAQBlock
  title="Frequently Asked Questions (अक्सर पूछे जाने वाले प्रश्न)"
  items={{[
    {{
      question: "क्या {place_hi} भाव में {lord_hi} होना सदा अशुभ या शुभ होता है?",
      answer: "नहीं, कोई भी स्थिति पूर्णतः शुभ या अशुभ नहीं होती। ग्रह की राशि स्थिति, दृष्टियाँ, नवांश बल तथा चल रही महादशा पर अंतिम फल निर्भर करता है।"
    }},
    {{
      question: "इस योग का फल कब सर्वाधिक महसूस होता है?",
      answer: "जब जातक के जीवन में {lord_hi} ग्रह की महादशा, अंतर्दशा या प्रत्यंतर्दशा चलती है, तब इसके फल प्रत्यक्ष रूप से दृष्टिगोचर होते हैं।"
    }}
  ]}}
/>
"""
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {target_file.relative_to(ROOT_DIR)}")

def generate_sun_article(place_num: int):
    place_en, place_hi, place_desc = HOUSE_NAMES[place_num]
    folder_name = "0601_Sun_in_all_Houses"
    file_name = f"0601{place_num:02d}_Sun_in_{place_en.split()[0]}_House.mdx"

    target_dir = HI_DIR / "06_Planet_in_Houses" / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / file_name

    content = f"""---
title: "Sun in {place_en} House ({place_hi} भाव में सूर्य) — Vedic Astrology Analysis"
description: "Comprehensive Vedic astrology analysis of Sun in {place_en} House ({place_hi} भाव में सूर्य): personality, career leadership, vitality, and classical remedies."
pubDate: '2026-08-17'
modifiedDate: '2026-08-17'
locale: 'hi'
sourceLocale: 'en'
author: 'AstroFusion Editorial'
keywords:
  - "Sun in {place_en.lower()} house"
  - "{place_hi} भाव में सूर्य"
  - "सूर्य {place_hi} भाव में"
  - "Sun in {place_en.lower()} house in Hindi"
  - "वैदिक ज्योतिष सूर्य फल"
  - "फलदीपिका"
  - "बृहत् जातक"
---

# {place_hi} भाव में सूर्य: तेज, नेतृत्व एवं प्रभाव (Sun in {place_en} House)

## Keywords: Sun in {place_en} House, {place_hi} भाव में सूर्य, वैदिक ज्योतिष, नेतृत्व, आत्म-सम्मान, {place_desc}, उपाय

## Executive Summary (मुख्य सारांश)

<AIBlufSummary>
वैदिक ज्योतिष में **सूर्य (राजा एवं आत्मा का कारक)** का कुण्डली के **{place_hi} भाव** ({place_desc}) में विराजमान होना जातक को प्रभावशाली व्यक्तित्व, दृढ़ संकल्प और विशिष्ट जीवन पथ प्रदान करता है। यह स्थिति जातक के जीवन के इस क्षेत्र में महत्वपूर्ण प्रतिष्ठा और प्रभाव स्थापित करती है।
</AIBlufSummary>

<KundaliChart
  title="{place_hi} भाव में सूर्य — Illustrative Chart"
  combinationLabel="Sun in {place_en} House ({place_hi} भाव में सूर्य)"
  lagnaRashi={{1}}
  placements={{[{{ planet: "Sun", house: {place_num}, isLordOf: 5 }}]}}
  highlightHouses={{[{place_num}]}}
  description="यह चित्रण मेष लग्न की कुण्डली के आधार पर {place_hi} भाव में सूर्य की स्थिति को दर्शाता है। आपकी व्यक्तिगत कुण्डली में लग्न के अनुसार सूर्य के प्रभाव भिन्न होंगे।"
  effects={{[
    "सूर्य का प्रभाव {place_hi} भाव के मुख्य कार्यक्षेत्र पर स्पष्ट रूप से दृष्टिगोचर होता है।",
    "आत्म-विश्वास, नेतृत्व क्षमता और स्वतंत्र कार्यशैली में वृद्धि।",
    "सूर्य की महादशा और अंतर्दशा काल में इस स्थिति के परिणाम अधिक प्रभावशाली होते हैं।"
  ]}}
  ctaText="Check Your Sun Placement"
  ctaHref="/hi/kundali"
/>

## Classical Shastra References (शास्त्रीय प्रमाण)

<BookReference
  book="PhalaDeepika"
  chapter="8"
  locale="hi"
  label="Phala Deepika — Chapter 8 (Sun in Houses)"
/>

<YogaDeepLink
  yogaId="HoroscopeDataListStatic:suninhouse{place_num}"
  label="{place_hi} भाव में सूर्य — Analyze in Your Personal Kundali"
  source="Phala Deepika & Saravali"
  locale="hi"
/>

## Core Astrological Dynamics (विस्तृत प्रभाव एवं फल)

### 1. व्यक्तित्व एवं जीवन ऊर्जा
सूर्य आत्मा, तेज और जीवनी शक्ति का प्रतिनिधि है। {place_hi} भाव में इसकी उपस्थिति जातक को एक ओजस्वी दृष्टिकोण और कार्यकुशलता प्रदान करती है।

### 2. करियर एवं नेतृत्व
इस भाव में सूर्य जातक को प्रशासनिक, प्रबंधकीय अथवा स्वतंत्र व्यवसाय में अग्रसर करता है। समाज और कार्यक्षेत्र में मान-सम्मान की प्राप्ति होती है।

### 3. संबंध एवं सामाजिक जीवन
सूर्य की स्थिति से जातक के सामाजिक संबंधों में गरिमा और स्पष्टता बनी रहती है। अहंकार के टकराव से बचकर सामंजस्य स्थापित करना फलदायी रहता है।

---

## Vedic Remedial Measures (शास्त्रीय उपाय)

1. **सूर्य अर्घ्य**: प्रतिदिन प्रातःकाल तांबे के पात्र से जल में रोली व लाल पुष्प डालकर सूर्य को अर्घ्य दें।
2. **आदित्य हृदय स्तोत्र**: रविवार के दिन आदित्य हृदय स्तोत्र का पाठ करने से आत्म-विश्वास और तेज में वृद्धि होती है।
3. **गायत्री मंत्र**: नित्य गायत्री मंत्र का 108 बार जप करें।

<FAQBlock
  title="Frequently Asked Questions (अक्सर पूछे जाने वाले प्रश्न)"
  items={{[
    {{
      question: "क्या {place_hi} भाव में सूर्य सदा शुभ फल देता है?",
      answer: "सूर्य की शुभता उसकी राशि स्थिति, मित्र/शत्रु दृष्टि तथा नवांश बल पर निर्भर करती है। मेष राशि में सूर्य उच्च तथा तुला में नीच का होता है।"
    }},
    {{
      question: "सूर्य के इस प्रभाव को कब सर्वाधिक अनुभव किया जा सकता है?",
      answer: "सूर्य की महादशा, अंतर्दशा या रविवार के गोचर काल में इसका प्रभाव विशेष रूप से सक्रिय रहता है।"
    }}
  ]}}
/>
"""
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated: {target_file.relative_to(ROOT_DIR)}")

def generate_p0_batch():
    print("Generating P0 Hindi Batch (8th Lord, 2nd Lord & Sun in Houses)...")
    # 1. 8th Lord in all 12 houses
    for place in range(1, 13):
        generate_lord_article(8, place)
    # 2. 2nd Lord in all 12 houses
    for place in range(1, 13):
        generate_lord_article(2, place)
    # 3. Sun in all 12 houses
    for place in range(1, 13):
        generate_sun_article(place)
    print("P0 Batch generation complete! Total: 36 articles generated.")

if __name__ == "__main__":
    generate_p0_batch()

