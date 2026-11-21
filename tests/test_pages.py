import json
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
# 발표 자료는 비공개 저장소 hanminy-slides로 옮겼다. 이 폴더들이 다시 생기면 공개돼 버린다.
MOVED = ['slides', 'working-notes', 'fes2026-physical-ai', 'fes2026-special-lecture', 'kict-seminar-202611', 'gist-colloquium-202611']


class PageTests(unittest.TestCase):
    def test_cards_for_pages_in_this_repo_point_at_real_files(self):
        config = json.loads((ROOT / 'sites.json').read_text(encoding='utf-8'))
        prefix = f"https://{config['owner']}.github.io/assets/"
        local = [s for s in config['extra_sites'] if s['url'].startswith(prefix)]
        self.assertTrue(local)
        for site in local:
            page = ROOT / 'assets' / unquote(urlsplit(site['url']).path).split('/assets/', 1)[1] / 'index.html'
            self.assertTrue(page.is_file(), f"{site['id']}: {site['url']}")

    def test_categories_are_the_agreed_four(self):
        config = json.loads((ROOT / 'sites.json').read_text(encoding='utf-8'))
        used = {s['category'] for s in config['extra_sites']} | {o['category'] for o in config['overrides'].values()}
        self.assertTrue(used <= {'연구 아카이브', '발표', '설명 자료', '개인'}, used)

    def test_slides_stay_out_of_the_public_site(self):
        for name in MOVED:
            self.assertFalse((ROOT / 'assets' / name).exists(), f'assets/{name}: 발표 자료는 hanminy-slides 저장소에 올린다')


if __name__ == '__main__':
    unittest.main()
