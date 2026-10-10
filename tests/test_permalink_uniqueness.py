"""Falsifier for the self-improvement-tha-c01280 permalink collision cure.

Before the cure, three truncated permalinks were claimed by seven level-3
``*_index.md`` documents (4+2+1 colliding), shadowing five indexes. The cure
keeps the live winner at each shared route and gives every shadowed index a
unique ``-<index title>`` suffixed permalink.
"""
import io
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
PERMALINK = re.compile(r"^permalink:\s*[\"']?([^\s\"'#]+)[\"']?\s*$", re.M)


def page_permalinks():
    out = {}
    for p in PAGES.glob("*.md"):
        m = FRONT_MATTER.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        pm = PERMALINK.search(m.group(1))
        if pm:
            out[p.name] = pm.group(1)
    return out


SHARED_SLUGS = {
    "/self-improvement-tha-c01280/",
    "/self-improvement-tha-c01280-habit/",
    "/self-improvement-tha-c01280-sleep/",
}

EXPECTED_CURED = {
    "/self-improvement-tha-c01280-consistency/",
    "/self-improvement-tha-c01280-useful-cues/",
    "/self-improvement-tha-c01280-design-around-temptation/",
    "/self-improvement-tha-c01280-habit-habit-timelines/",
    "/self-improvement-tha-c01280-sleep-sleep-and-focus/",
}


class TestPermalinkUniqueness(unittest.TestCase):
    def test_all_permalinks_unique(self):
        pls = page_permalinks()
        counts = Counter(pls.values())
        dups = {k: v for k, v in counts.items() if v > 1}
        owners = {k: sorted(n for n, v in pls.items() if v == k) for k in dups}
        self.assertEqual({}, owners)

    def test_shared_family_slugs_claimed_by_one_document(self):
        pls = page_permalinks()
        for slug in SHARED_SLUGS:
            owners = sorted(n for n, v in pls.items() if v == slug)
            self.assertEqual(1, len(owners), f"{slug} claimed by {owners}")

    def test_expected_cured_index_routes_exist(self):
        pls = set(page_permalinks().values())
        self.assertEqual(set(), EXPECTED_CURED - pls)

    def test_manifest_canonical_routes_for_cured_indexes(self):
        # The manifest predates the cure and carries pre-existing drift on
        # other pages; pin only that the five cured entries now carry the
        # new permalinks in their canonical_url routes.
        manifest = json.loads(io.open(ROOT / "phoenix-manifest.json", encoding="utf-8").read())
        cured_lids = {
            "self-improvement-tha-c01280-consistency-not-perf-a22660:index": "/self-improvement-tha-c01280-consistency/",
            "self-improvement-tha-c01280-environmental-cues-e06b07:index": "/self-improvement-tha-c01280-useful-cues/",
            "self-improvement-tha-c01280-environment-design-133edb:index": "/self-improvement-tha-c01280-design-around-temptation/",
            "self-improvement-tha-c01280-habit-formation-time-49cd57:index": "/self-improvement-tha-c01280-habit-habit-timelines/",
            "self-improvement-tha-c01280-sleep-attention-c3b951:index": "/self-improvement-tha-c01280-sleep-sleep-and-focus/",
        }
        bad = []
        for page in manifest.get("pages", []):
            lid = page.get("logical_id")
            if lid in cured_lids:
                route = "/" + (page.get("canonical_url") or "").split("/", 3)[-1].split("/", 1)[-1]
                if route != cured_lids[lid]:
                    bad.append((lid, route, cured_lids[lid]))
        self.assertEqual([], bad)

    def test_index_bodies_link_only_existing_routes(self):
        existing = set(page_permalinks().values())
        dangling = []
        for p in PAGES.glob("*_index.md"):
            for m in re.finditer(r"\{\{\s*'(/[^']*?)'\s*\|\s*relative_url", p.read_text(encoding="utf-8", errors="replace")):
                if m.group(1) not in existing:
                    dangling.append((p.name, m.group(1)))
        self.assertEqual([], dangling)


if __name__ == "__main__":
    unittest.main()
