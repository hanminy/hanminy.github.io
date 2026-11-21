"""Build a static directory from public GitHub Pages repositories, plus listed login-only sites."""
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
        # 로그인해야 열리는 사이트는 sites.json의 private_hosts에 적어 둔 주소만 허용한다.
        allowed = config.get('private_hosts', []) if site.get('private') else [f'{owner}.github.io']
        if url.scheme != 'https' or url.hostname not in allowed or url.username:
            raise ValueError(f'Unexpected site URL: {site["url"]}')
        if site['id'] in seen:
            raise ValueError('Duplicate site id')
        seen.add(site['id'])
    return sorted(sites, key=lambda s: (s.get('order', 100), s['title'].casefold()))


def reachable(site):
    if site.get('private'):
        return True  # 로그인 화면으로 넘어가므로 열리는지 확인할 수 없다
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
    text = ' '.join(str(site.get(k, '')) for k in ('title', 'description', 'category', 'label', 'id')) + ' ' + ' '.join(site.get('tags', []))
    private = bool(site.get('private'))
    where = '로그인 필요 · ' + urlsplit(site['url']).hostname if private else urlsplit(site['url']).path.strip('/')
    lock = '<span class="lock"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1.5"/><path d="M5.2 7V5a2.8 2.8 0 0 1 5.6 0v2"/></svg>비공개</span>' if private else ''
    tags = ''.join(f'<li>{esc(t)}</li>' for t in site.get('tags', []))
    tags = f'<ul class="card-tags">{tags}</ul>' if tags else ''
    if private:
        classes += ' private'
    if site.get('wide'):
        classes += ' wide'
    return f'''<a class="{classes}" href="{esc(site['url'])}"{' title="로그인한 사람만 볼 수 있습니다"' if private else ''} data-category="{esc(site['category'])}" data-search="{esc(text)}">
  <div class="card-top"><span class="card-label">{esc(site.get('label', 'WEBSITE'))}</span><span class="card-number">{index:02d}</span></div>
  <div class="card-body">{lock}<h4>{esc(site['title'])}</h4><p>{esc(site['description'])}</p>{tags}</div>
  <div class="card-bottom"><span>{esc(where)}</span><span class="arrow" aria-hidden="true">↗</span></div>
</a>'''


def grouped(sites, config):
    """분류별로 묶는다. sites.json의 groups 순서를 따르고, 거기 없는 분류는 뒤에 붙인다."""
    notes = {g['name']: g.get('note', '') for g in config.get('groups', [])}
    names = [n for n in notes if any(s['category'] == n for s in sites)]
    names += [n for n in dict.fromkeys(s['category'] for s in sites) if n not in notes]
    return [(n, notes.get(n, ''), [s for s in sites if s['category'] == n]) for n in names]


def sections(groups):
    parts, index = [], 0
    for number, (name, note, members) in enumerate(groups, 1):
        cards = []
        for site in members:
            index += 1
            cards.append(card(site, index))
        note_html = f'<p>{esc(note)}</p>' if note else ''
        parts.append(f'''<section class="group" id="g{number}" aria-labelledby="g{number}-title">
<div class="group-head"><h3 class="group-title" id="g{number}-title">{esc(name)}</h3>{note_html}<span class="group-count">{len(members)}</span></div>
<div class="site-grid{' four' if len(members) == 4 else ''}">
{chr(10).join(cards)}
</div>
</section>''')
    return '\n'.join(parts)


def build(repositories, config, output, check_urls=True):
    sites = collect(repositories, config)
    if check_urls:
        sites = [s for s in sites if reachable(s)]
    if not sites:
        raise ValueError('Refusing to deploy an empty directory')
    groups = grouped(sites, config)
    categories = [name for name, _, _ in groups]
    buttons = ''.join(f'<a class="filter" href="#g{number}">{esc(name)} <span>{len(members)}</span></a>' for number, (name, _, members) in enumerate(groups, 1))
    template = (ROOT / 'src/template.html').read_text()
    replacements = {
        '{{CARDS}}': sections(groups),
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
