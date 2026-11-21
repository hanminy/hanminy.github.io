import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from build import collect, card


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
        self.assertIn('로그인 필요', card(result[0], 1))


if __name__ == '__main__':
    unittest.main()
