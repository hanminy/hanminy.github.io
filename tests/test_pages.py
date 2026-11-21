import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK_PAGES = [ROOT / 'assets/personal/index.html']
# 발표 자료는 비공개 저장소 hanminy-slides로 옮겼다. 이 폴더들이 다시 생기면 공개돼 버린다.
MOVED = ['slides', 'working-notes', 'fes2026-physical-ai', 'fes2026-special-lecture', 'kict-seminar-202611', 'gist-colloquium-202611']


class PageTests(unittest.TestCase):
    def test_every_link_and_image_exists(self):
        for page in LINK_PAGES:
            text = page.read_text(encoding='utf-8')
            refs = re.findall(r'(?:href|src)="([^"#]+)"', text)
            self.assertTrue(refs)
            for ref in refs:
                url = urlsplit(ref)
                if url.scheme:
                    self.assertEqual((url.scheme, url.hostname), ('https', 'hanminy.github.io'), ref)
                    continue
                if ref.startswith('/'):
                    continue  # site root, built by src/build.py
                target = (page.parent / unquote(url.path)).resolve()
                if ref.endswith('/'):
                    target = target / 'index.html'
                self.assertTrue(target.is_file(), f'{page.parent.name} missing: {ref}')

    def test_slides_stay_out_of_the_public_site(self):
        for name in MOVED:
            self.assertFalse((ROOT / 'assets' / name).exists(), f'assets/{name}: 발표 자료는 hanminy-slides 저장소에 올린다')


if __name__ == '__main__':
    unittest.main()
