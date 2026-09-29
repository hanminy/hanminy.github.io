"""Build a static directory from public GitHub Pages repositories only."""
import argparse
import html
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def public_repositories(owner):
    repositories = []
    for page in range(1, 101):
        # This public endpoint never includes the owner's private repositories.
        request = Request(f'https://api.github.com/users/{owner}/repos?per_page=100&page={page}', headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'hanminy-site-directory'})
        token = os.environ.get('GH_TOKEN')
        if token:
            request.add_header('Authorization', f'Bearer {token}')
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        repositories.extend(batch)
        if len(batch) < 100:
            return repositories
    raise RuntimeError('Repository pagination limit exceeded')


def collect(repositories, config):
    owner = config['owner']
    sites = []
    for repo in repositories:
        name = repo['name']
        if repo.get('private') or not repo.get('has_pages') or name in config.get('exclude', []) or name.lower() == f'{owner}.github.io'.lower():
            continue
        site = {
            'id': name, 'title': name, 'description': repo.get('description') or '새롭게 공개한 사이트를 방문해 보세요.',
            'url': f'https://{owner}.github.io/{name}/', 'category': '기타',
            'label': 'WEBSITE', 'order': 100, 'featured': False,
        }
        site.update(config.get('overrides', {}).get(name, {}))
        sites.append(site)
    sites.extend(config.get('extra_sites', []))
    seen = set()
    for site in sites:
        url = urlsplit(site['url'])
        if url.scheme != 'https' or url.hostname != f'{owner}.github.io' or url.username:
            raise ValueError(f'Unexpected public site URL: {site["url"]}')
        if site['id'] in seen:
            raise ValueError('Duplicate site id')
        seen.add(site['id'])
    return sorted(sites, key=lambda s: (s.get('order', 100), s['title'].casefold()))


def reachable(site):
    try:
        request = Request(site['url'], headers={'User-Agent': 'hanminy-site-directory'}, method='HEAD')
        with urlopen(request, timeout=30) as response:
            return response.status == 200
    except HTTPError as error:
        if error.code == 404:
            if site.get('order', 100) < 100:
                raise RuntimeError(f'Configured site is missing: {site["url"]}') from error
            print(f'Not yet published; skip {site["id"]}')
            return False
        raise


def esc(value):
    return html.escape(str(value), quote=True)


def card(site, index):
    classes = 'site-card featured' if site.get('featured') else 'site-card'
    text = ' '.join(str(site.get(k, '')) for k in ('title', 'description', 'category', 'label', 'id'))
    return f'''<a class="{classes}" href="{esc(site['url'])}" data-category="{esc(site['category'])}" data-search="{esc(text)}">
  <div class="card-top"><span class="card-label">{esc(site.get('label', 'WEBSITE'))}</span><span class="card-number">{index:02d}</span></div>
  <div class="card-body"><span class="category">{esc(site['category'])}</span><h3>{esc(site['title'])}</h3><p>{esc(site['description'])}</p></div>
  <div class="card-bottom"><span>{esc(urlsplit(site['url']).path.strip('/'))}</span><span class="arrow" aria-hidden="true">↗</span></div>
</a>'''


def build(repositories, config, output, check_urls=True):
    sites = collect(repositories, config)
    if check_urls:
        sites = [s for s in sites if reachable(s)]
    if not sites:
        raise ValueError('Refusing to deploy an empty directory')
    categories = list(dict.fromkeys(s['category'] for s in sites))
    buttons = '<button type="button" class="filter active" data-category="all" aria-pressed="true">전체 <span>' + str(len(sites)) + '</span></button>'
    buttons += ''.join(f'<button type="button" class="filter" data-category="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in categories)
    template = (ROOT / 'src/template.html').read_text()
    replacements = {
        '{{CARDS}}': '\n'.join(card(s, i) for i, s in enumerate(sites, 1)),
        '{{FILTERS}}': buttons, '{{COUNT}}': str(len(sites)),
        '{{UPDATED}}': datetime.now(timezone.utc).strftime('%Y.%m.%d'),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(template, encoding='utf-8')
    (output / 'sites.json').write_text(json.dumps(sites, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / '.nojekyll').touch()
    shutil.copytree(ROOT / 'assets', output / 'assets', dirs_exist_ok=True)
    print(f'Built {len(sites)} sites across {len(categories)} categories')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repositories', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    config = json.loads((ROOT / 'sites.json').read_text())
    repositories = json.loads(args.repositories.read_text()) if args.repositories else public_repositories(config['owner'])
    build(repositories, config, args.output)
