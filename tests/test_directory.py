import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from build import collect, card, grouped, sections


class DirectoryTests(unittest.TestCase):
    def test_new_pages_appear_but_private_nonpages_and_self_do_not(self):
        repos = [
            {'name': 'new-site', 'has_pages': True},
            {'name': 'private-site', 'has_pages': True, 'private': True},
            {'name': 'code-only', 'has_pages': False},
            {'name': 'hanminy.github.io', 'has_pages': True},
            {'name': 'hidden-site', 'has_pages': True},
        ]
        result = collect(repos, {'owner': 'hanminy', 'exclude': ['hidden-site']})
        self.assertEqual([s['id'] for s in result], ['new-site'])
        self.assertEqual(result[0]['url'], 'https://hanminy.github.io/new-site/')

    def test_subdirectory_override_and_extra_site(self):
        config = {'owner': 'hanminy', 'overrides': {'blog': {'url': 'https://hanminy.github.io/blog/notes/', 'order': 1}}, 'extra_sites': [{'id': 'guide', 'title': 'Guide', 'url': 'https://hanminy.github.io/blog/guide/'}]}
        result = collect([{'name': 'blog', 'has_pages': True}], config)
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]['url'].endswith('/notes/'))

    def test_unexpected_link_is_rejected_and_metadata_escaped(self):
        with self.assertRaises(ValueError):
            collect([], {'owner': 'hanminy', 'extra_sites': [{'id': 'bad', 'url': 'javascript:alert(1)'}]})
        record = collect([{'name': 'test', 'has_pages': True, 'description': '<script>bad()</script>'}], {'owner': 'hanminy'})[0]
        rendered = card(record, 1)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_private_site_needs_a_listed_host_and_shows_login_note(self):
        site = {'id': 'slides', 'title': 'Slides', 'description': 'd', 'category': 'x', 'url': 'https://slides.example.dev/slides/', 'private': True}
        with self.assertRaises(ValueError):
            collect([], {'owner': 'hanminy', 'extra_sites': [dict(site)]})
        with self.assertRaises(ValueError):  # private 표시가 없으면 다른 주소는 받지 않는다
            collect([], {'owner': 'hanminy', 'private_hosts': ['slides.example.dev'], 'extra_sites': [{k: v for k, v in site.items() if k != 'private'}]})
        result = collect([], {'owner': 'hanminy', 'private_hosts': ['slides.example.dev'], 'extra_sites': [dict(site)]})
        rendered = card(result[0], 1)
        self.assertIn('로그인 필요', rendered)
        self.assertIn('class="lock"', rendered)
        public = collect([{'name': 'open', 'has_pages': True}], {'owner': 'hanminy'})[0]
        self.assertNotIn('class="lock"', card(public, 1))

    def test_cards_are_grouped_in_configured_order_and_unknown_categories_go_last(self):
        sites = [{'id': i, 'title': i, 'description': 'd', 'url': 'https://hanminy.github.io/' + i + '/', 'category': c} for i, c in (('a', '개인'), ('b', '기타'), ('c', '연구 아카이브'), ('d', '연구 아카이브'))]
        config = {'groups': [{'name': '연구 아카이브', 'note': 'n'}, {'name': '발표'}, {'name': '개인'}]}
        groups = grouped(sites, config)
        self.assertEqual([(name, len(members)) for name, _, members in groups], [('연구 아카이브', 2), ('개인', 1), ('기타', 1)])
        rendered = sections(groups)
        self.assertEqual(rendered.count('class="group"'), 3)
        self.assertEqual(rendered.count('class="site-card'), 4)
        self.assertLess(rendered.index('>01<'), rendered.index('>04<'))



if __name__ == '__main__':
    unittest.main()
