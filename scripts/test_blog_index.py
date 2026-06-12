import unittest
import os
import re
import json

# Import functions from generate_blog_index_tree
from generate_blog_index_tree import (
    clean_name,
    slugify,
    clean_text_for_summary,
    extract_sentences,
    extract_sections,
    get_normalized_category_name
)

class TestBlogIndexGeneration(unittest.TestCase):

    def test_clean_name(self):
        self.assertEqual(clean_name("01_Rasi"), "Rasi")
        self.assertEqual(clean_name("06_Planet_in_Houses"), "Planet in Houses")
        self.assertEqual(clean_name("07_House_Lord_Placements "), "House Lord Placements")

    def test_slugify(self):
        self.assertEqual(slugify("Mesha Rashi"), "mesha-rashi")
        self.assertEqual(slugify("Mars in 1st House"), "mars-in-1st-house")
        self.assertEqual(slugify("sun-mars-conjunction"), "sun-mars-conjunction")

    def test_get_normalized_category_name(self):
        self.assertEqual(get_normalized_category_name("09_Lords_in_Houses"), "Lord in Houses")
        self.assertEqual(get_normalized_category_name("10_Lord_in_Houses"), "Lord in Houses")
        self.assertEqual(get_normalized_category_name("07_House_Lord_Placements"), "Lord in Houses")
        self.assertEqual(get_normalized_category_name("08_Conjunctions"), "Planets Conjunctions")
        self.assertEqual(get_normalized_category_name("11_Planets_Conjunctions"), "Planets Conjunctions")
        self.assertEqual(get_normalized_category_name("04_DashaSystem"), "Dasha System")
        self.assertEqual(get_normalized_category_name("01_Rasi"), "Rasi")

    def test_clean_text_for_summary(self):
        sample_mdx = """
        <FAQBlock faqs={[{question: "Q1", answer: "A1"}]} />
        **Bold Text** and _italic text_.
        | Table | Header |
        |---|---|
        - Item 1
        - Item 2
        1. Item 3
        """
        cleaned = clean_text_for_summary(sample_mdx)
        self.assertNotIn("<FAQBlock", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("|", cleaned)
        self.assertIn("Bold Text and italic text", cleaned)

    def test_extract_sentences(self):
        text = "This is the first sentence. Here is the second one. And a third."
        two_sentences = extract_sentences(text, 2)
        self.assertEqual(two_sentences, "This is the first sentence. Here is the second one.")

    def test_extract_sections_structural_filtering(self):
        content = """
## Table of Contents
1. [Intro](#intro)

## Keywords
Mesha Rashi, Mars

## Summary of Article
This is an overview summary.

## Introduction to Mesha
<AIBlufSummary>
Vedic astrology introduction to Mesha Rashi.
</AIBlufSummary>
More content here.

## Frequently Asked Questions
FAQ answers.
"""
        sections = extract_sections(content, "Mesha Guide")
        headings = [s["heading"] for s in sections]
        
        # Verify that structural sections were filtered out
        self.assertNotIn("Table of Contents", headings)
        self.assertNotIn("Keywords", headings)
        self.assertNotIn("Summary of Article", headings)
        self.assertNotIn("Frequently Asked Questions", headings)
        
        # Verify that valid sections remain
        self.assertIn("Introduction to Mesha", headings)
        intro_sec = [s for s in sections if s["heading"] == "Introduction to Mesha"][0]
        self.assertEqual(intro_sec["summary"], "Vedic astrology introduction to Mesha Rashi.")

    def test_generated_index_tree_integrity(self):
        # Smoke and integrity check on the generated blog-index-tree.json file itself
        index_path = os.path.join(os.path.dirname(__file__), '..', 'blog-index-tree.json')
        self.assertTrue(os.path.exists(index_path), "blog-index-tree.json does not exist")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        for category in data:
            self.assertIn("category", category)
            self.assertIn("summary", category)
            self.assertIn("children", category)
            self.assertGreater(len(category["children"]), 0)
            
            # Ensure category names do not have duplicate strings or spaces
            self.assertNotEqual(category["category"], "Remedies")  # Filtered out because it is empty
            self.assertNotIn(category["category"], ["Lords in Houses", "House Lord Placements"]) # Merged
            
            for doc in category["children"]:
                self.assertIn("title", doc)
                self.assertIn("slug", doc)
                self.assertIn("summary", doc)
                self.assertIn("sections", doc)
                
                # Check description completeness rules
                self.assertGreaterEqual(len(doc["summary"]), 80, f"Doc '{doc['title']}' summary is too short")
                
                for sec in doc["sections"]:
                    self.assertIn("id", sec)
                    self.assertIn("heading", sec)
                    self.assertIn("summary", sec)
                    self.assertTrue(sec["id"].startswith("sec-"))
                    
                    # Ensure no structural sections leaked in
                    lower_heading = sec["heading"].lower()
                    self.assertNotIn("table of contents", lower_heading)
                    self.assertNotIn("keywords", lower_heading)

if __name__ == "__main__":
    unittest.main()
