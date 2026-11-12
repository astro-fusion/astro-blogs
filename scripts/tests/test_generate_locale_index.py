"""Tests for scripts/generate_locale_index.py (full rebuild and the --roots refresh)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generate_locale_index as g  # noqa: E402


def write(root: Path, rel: str, title: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntitle: "{title}"\ndescription: "About {title}."\n---\n\nBody.\n', encoding="utf-8")


def read(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


OUTPUTS = ["_meta.json", "_multilang_meta.json", "blog-en-index-tree.json", "blog-hi-index-tree.json", "blog-ne-index-tree.json"]


class FullRebuildTest(unittest.TestCase):
    def test_records_available_locales_and_orders_en_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "en/18_Vastu/1801_Intro/180101_A.mdx", "A")
            write(root, "hi/18_Vastu/1801_Intro/180101_A.mdx", "ए")
            write(root, "en/22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "Bed")
            write(root, "ne/99_Only_Ne/9901_X/990101_x.mdx", "X")
            g.generate_indexes(root=root, log=lambda _: None)
            meta = read(root, "_meta.json")
            self.assertEqual(meta["locales"], ["en", "hi", "ne"])
            self.assertEqual(meta["totalArticles"], 3)
            self.assertEqual(
                list(meta["articles"]),
                [
                    "18_Vastu/1801_Intro/180101_A.mdx",
                    "22_Home_Living/2201_Room_by_Room/220101_bed.mdx",
                    "99_Only_Ne/9901_X/990101_x.mdx",
                ],
            )
            self.assertEqual(meta["articles"]["18_Vastu/1801_Intro/180101_A.mdx"]["availableLocales"], ["en", "hi"])
            self.assertEqual(
                meta["articles"]["22_Home_Living/2201_Room_by_Room/220101_bed.mdx"],
                {"path": "22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "availableLocales": ["en"], "title": "Bed"},
            )
            self.assertEqual(read(root, "_multilang_meta.json"), meta["articles"])
            self.assertEqual(read(root, "blog-hi-index-tree.json")["count"], 1)


class RootsRefreshTest(unittest.TestCase):
    def _seed(self, root: Path) -> None:
        write(root, "en/18_Vastu/1801_Intro/180101_A.mdx", "A")
        write(root, "en/18_Vastu/1806_Plot Selection/180601_P.mdx", "P")
        write(root, "hi/18_Vastu/1801_Intro/180101_A.mdx", "ए")
        write(root, "en/19_Medical/1901_X/190101_x.mdx", "M")
        g.generate_indexes(root=root, log=lambda _: None)

    def test_adds_new_roots_and_leaves_every_other_entry_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed(root)
            # Unrelated edits that a --roots run must not pick up.
            write(root, "en/18_Vastu/1801_Intro/180101_A.mdx", "A renamed elsewhere")
            write(root, "en/12_Articles/1201_New/120101_n.mdx", "Not yet indexed")
            before = {name: (root / name).read_text(encoding="utf-8") for name in OUTPUTS}
            write(root, "en/22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "Bed")
            write(root, "en/22_Home_Living/2203_Light_Air_and_Comfort/220301_light.mdx", "Light")
            write(root, "en/23_Interior_Design/2301_Layout_and_Furniture/230101_clear.mdx", "Clear")

            g.generate_indexes(root=root, roots=["22_Home_Living", "23_Interior_Design"], log=lambda _: None)
            meta = read(root, "_meta.json")
            keys = list(meta["articles"])
            self.assertEqual(
                keys,
                [
                    "18_Vastu/1801_Intro/180101_A.mdx",
                    "18_Vastu/1806_Plot Selection/180601_P.mdx",
                    "19_Medical/1901_X/190101_x.mdx",
                    "22_Home_Living/2201_Room_by_Room/220101_bed.mdx",
                    "22_Home_Living/2203_Light_Air_and_Comfort/220301_light.mdx",
                    "23_Interior_Design/2301_Layout_and_Furniture/230101_clear.mdx",
                ],
            )
            self.assertEqual(meta["totalArticles"], 6)
            self.assertEqual(meta["articles"]["18_Vastu/1801_Intro/180101_A.mdx"]["title"], "A")
            self.assertNotIn("12_Articles/1201_New/120101_n.mdx", meta["articles"])
            self.assertEqual(meta["articles"]["23_Interior_Design/2301_Layout_and_Furniture/230101_clear.mdx"]["availableLocales"], ["en"])
            # hi and ne have no file under the new roots: their trees are unchanged.
            self.assertEqual((root / "blog-hi-index-tree.json").read_text(encoding="utf-8"), before["blog-hi-index-tree.json"])
            self.assertEqual((root / "blog-ne-index-tree.json").read_text(encoding="utf-8"), before["blog-ne-index-tree.json"])
            en = read(root, "blog-en-index-tree.json")
            self.assertEqual(en["count"], 6)
            self.assertEqual(en["articles"][0]["title"], "A")

    def test_matches_a_full_rebuild_when_nothing_else_changed_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._seed(root)
            write(root, "en/22_Home_Living/2202_Small_Homes_and_Flats/220201_2bhk.mdx", "2BHK")
            write(root, "hi/22_Home_Living/2202_Small_Homes_and_Flats/220201_2bhk.mdx", "2बीएचके")
            g.generate_indexes(root=root, roots=["22_Home_Living"], log=lambda _: None)
            partial = {name: (root / name).read_text(encoding="utf-8") for name in OUTPUTS}
            g.generate_indexes(root=root, roots=["22_Home_Living"], log=lambda _: None)
            again = {name: (root / name).read_text(encoding="utf-8") for name in OUTPUTS}
            self.assertEqual(again, partial)
            g.generate_indexes(root=root, log=lambda _: None)
            full = {name: (root / name).read_text(encoding="utf-8") for name in OUTPUTS}
            self.assertEqual(full, partial)
            self.assertEqual(read(root, "_meta.json")["articles"]["22_Home_Living/2202_Small_Homes_and_Flats/220201_2bhk.mdx"]["availableLocales"], ["en", "hi"])

    def test_drops_entries_whose_file_is_gone_under_a_refreshed_root_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "en/22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "Bed")
            write(root, "en/22_Home_Living/2201_Room_by_Room/220102_gone.mdx", "Gone")
            write(root, "en/19_Medical/1901_X/190101_x.mdx", "M")
            g.generate_indexes(root=root, log=lambda _: None)
            (root / "en/22_Home_Living/2201_Room_by_Room/220102_gone.mdx").unlink()
            (root / "en/19_Medical/1901_X/190101_x.mdx").unlink()
            g.generate_indexes(root=root, roots=["22_Home_Living"], log=lambda _: None)
            keys = list(read(root, "_meta.json")["articles"])
            self.assertEqual(keys, ["19_Medical/1901_X/190101_x.mdx", "22_Home_Living/2201_Room_by_Room/220101_bed.mdx"])

    def test_rejects_a_root_with_a_path_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                g.generate_indexes(root=Path(tmp), roots=["../etc"], log=lambda _: None)

    def test_requires_existing_indexes_for_a_roots_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "en/22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "Bed")
            with self.assertRaises(FileNotFoundError):
                g.generate_indexes(root=root, roots=["22_Home_Living"], log=lambda _: None)


class TrackedOnlyTest(unittest.TestCase):
    def test_leaves_out_files_git_does_not_track(self):
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "en/22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "Bed")
            write(root, "en/19_Medical/1901_X/190101_x.mdx", "M")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "en"], cwd=root, check=True)
            g.generate_indexes(root=root, log=lambda _: None)
            # A draft translation that is not in git yet.
            write(root, "hi/22_Home_Living/2201_Room_by_Room/220101_bed.mdx", "बिस्तर")
            write(root, "en/22_Home_Living/2201_Room_by_Room/220102_draft.mdx", "Draft")
            g.generate_indexes(root=root, roots=["22_Home_Living"], tracked_only=True, log=lambda _: None)
            meta = read(root, "_meta.json")["articles"]
            self.assertEqual(list(meta), ["19_Medical/1901_X/190101_x.mdx", "22_Home_Living/2201_Room_by_Room/220101_bed.mdx"])
            self.assertEqual(meta["22_Home_Living/2201_Room_by_Room/220101_bed.mdx"]["availableLocales"], ["en"])
            self.assertEqual(read(root, "blog-hi-index-tree.json")["count"], 0)
            g.generate_indexes(root=root, roots=["22_Home_Living"], log=lambda _: None)
            self.assertEqual(read(root, "_meta.json")["articles"]["22_Home_Living/2201_Room_by_Room/220101_bed.mdx"]["availableLocales"], ["en", "hi"])


if __name__ == "__main__":
    unittest.main()
