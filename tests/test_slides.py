import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'assets/slides/index.html'


class SlideListTests(unittest.TestCase):
    def test_every_link_and_image_exists(self):
        text = PAGE.read_text(encoding='utf-8')
        refs = re.findall(r'(?:href|src)="([^"#]+)"', text)
        self.assertTrue(refs)
        for ref in refs:
            url = urlsplit(ref)
            if url.scheme:
                self.assertEqual((url.scheme, url.hostname), ('https', 'hanminy.github.io'), ref)
                continue
            if ref.startswith('/'):
                continue  # site root, built by src/build.py
            target = (PAGE.parent / unquote(url.path)).resolve()
            if ref.endswith('/'):
                target = target / 'index.html'
            self.assertTrue(target.is_file(), f'missing: {ref}')

    def test_filter_counts_match_entries(self):
        text = PAGE.read_text(encoding='utf-8')
        kinds = re.findall(r'<li class="deck" data-kind="(\w+)"', text)
        counts = dict(re.findall(r'data-kind="(\w+)" aria-pressed="\w+">[^<]*<span>(\d+)</span>', text))
        self.assertEqual(int(counts['all']), len(kinds))
        for kind in ('talk', 'self'):
            self.assertEqual(int(counts[kind]), kinds.count(kind))


if __name__ == '__main__':
    unittest.main()
