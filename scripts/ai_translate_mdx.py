#!/usr/bin/env python3
"""
AI-Powered MDX Translator for AstroFusion
-----------------------------------------
Translates English MDX articles to Hindi (hi) or Nepali (ne) while 
strictly preserving YAML frontmatter keys, React/MDX components, 
and markdown formatting.

Usage:
  python ai_translate_mdx.py --input ../en/01_Rasi/0101_Mesha.mdx --lang hi --output ../hi/01_Rasi/0101_Mesha.mdx
"""

import os
import argparse
import time
import requests
import json
from pathlib import Path

# Set your API Key in the environment before running
# e.g., export GEMINI_API_KEY="your-api-key"
# Using Gemini 1.5 Pro or Flash as the default translation engine for large context window & reasoning
API_KEY = os.environ.get("GEMINI_API_KEY")

def translate_mdx(content: str, target_lang: str) -> str:
    if not API_KEY:
        print("WARNING: GEMINI_API_KEY not found. Using dry-run/mock output.")
        # In a real run, it would fail here. For demonstration, we'll return a mock if no key.
        # raise ValueError("GEMINI_API_KEY environment variable is required.")
        return content.replace("Mesha Rashi", f"[{target_lang.upper()} TRANSLATION: Mesha Rashi]")

    lang_map = {
        "hi": "Hindi",
        "ne": "Nepali"
    }
    language_name = lang_map.get(target_lang, target_lang)

    system_instruction = f"""
You are an expert Vedic Astrologer and a highly skilled technical translator native in {language_name}.
Your task is to translate an English MDX (Markdown + React components) file into {language_name}.

CRITICAL RULES:
1. PRESERVE ALL MDX/REACT COMPONENTS: Do not translate component names (e.g., <KundaliChart>, <AIBlufSummary>, <BookShlokaSnippet>).
2. PRESERVE ALL COMPONENT PROPS: Do not translate property names like `title=`, `description=`, `lagnaRashi=`, etc.
3. TRANSLATE PROP VALUES ONLY IF THEY ARE NATURAL LANGUAGE: 
   - <KundaliChart description="Translate this"> -> <KundaliChart description="[Translated text]">
   - DO NOT translate IDs or paths (e.g., `ctaHref="/kundali"`, `yogaId="rashi1"`).
4. PRESERVE YAML FRONTMATTER: Do not translate the keys (title, description, pubDate, etc.). ONLY translate the values of `title`, `description`, and `keywords`. Leave `locale`, `author`, `image` exactly as they are.
5. VEDIC ASTROLOGY LEXICON: Use accurate Sanskrit/Vedic terminology in {language_name} (e.g., Aries = मेष (Mesha), Mars = मंगल (Mangal), Ascendant = लग्न (Lagna)).
6. OUTPUT RAW MDX: Return ONLY the translated file content. Do not wrap it in markdown code blocks (e.g., no ```mdx ... ```). Just the raw text.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "parts": [{"text": f"Translate the following MDX file into {language_name}:\n\n{content}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2, # Low temperature for accurate translation
        }
    }

    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    data = response.json()
    translated_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    # Strip markdown block if the LLM accidentally added it
    if translated_text.startswith("```mdx"):
        translated_text = translated_text[6:]
    elif translated_text.startswith("```markdown"):
        translated_text = translated_text[11:]
    elif translated_text.startswith("```"):
        translated_text = translated_text[3:]
        
    if translated_text.endswith("```"):
        translated_text = translated_text[:-3]
        
    return translated_text.strip()

def main():
    parser = argparse.ArgumentParser(description="AI Translate MDX Files")
    parser.add_argument("--input", required=True, help="Path to source English MDX file")
    parser.add_argument("--lang", required=True, choices=["hi", "ne"], help="Target language code (hi or ne)")
    parser.add_argument("--output", required=True, help="Path to save translated MDX file")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return
        
    print(f"Reading {input_path}...")
    source_content = input_path.read_text(encoding="utf-8")
    
    print(f"Translating to {args.lang} using AI... (This may take 10-30 seconds)")
    try:
        translated_content = translate_mdx(source_content, args.lang)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write translated file
        output_path.write_text(translated_content, encoding="utf-8")
        print(f"✅ Successfully translated and saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")

if __name__ == "__main__":
    main()
