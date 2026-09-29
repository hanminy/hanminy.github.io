# hanminy.github.io

[공개 메인 페이지](https://hanminy.github.io/) — 연구 자료, 개발·실험, 일상 사이트로 연결하는 정적 홈페이지.

## 새 사이트 추가

- **새 공개 저장소의 GitHub Pages**: 별도 등록 없이 다음 자동 배포에서 발견한다. 매시간 17분에 공개 저장소 목록을 확인한다. GitHub의 실행 대기 때문에 실제 시각은 지연될 수 있다.
- **이름·설명·분류·순서 변경**: `sites.json`의 `overrides`에 저장소 이름을 키로 등록한다.
- **같은 저장소의 다른 하위 페이지**: `extra_sites`에 고유 `id`, `title`, `description`, `url`, `category`, `label`, `order`를 추가한다.
- **제외할 저장소**: `exclude` 배열에 저장소 이름을 넣는다.
- **즉시 갱신**: Actions → Refresh site directory and deploy → Run workflow. 설정을 main에 push해도 배포한다.

GitHub Pages가 켜진 공개 저장소만 조회한다. 비공개 저장소, 일반 코드 저장소, 이 홈페이지 자체는 목록에 넣지 않는다. 새 사이트의 주소가 아직 404면 다음 실행에서 다시 확인한다. 기존에 설정한 주요 링크가 깨지거나 API 요청이 실패하면 배포를 중단하고 기존 공개본을 유지한다.

MarkTL의 실제 진입점은 `/marktl-blog/marktl/`이다. KMM 스터디는 같은 저장소의 별도 경로 `/marktl-blog/kmm/`로 등록했다. 사이트 단위 목록이며 MarkTL의 개별 게시물까지 펼치지는 않는다.

## 구조와 검증

- `sites.json`: 표시 이름과 하위 경로 설정
- `src/build.py`: 공개 저장소 발견, 주소 확인, HTML 생성 (Python 표준 라이브러리)
- `src/template.html`, `assets/`: 반응형 화면, 검색·분류
- `.github/workflows/pages.yml`: push·매시간·수동 갱신과 Pages 배포
- `tests/`: 새 사이트 자동 발견, 공개 범위, 하위 경로, 링크·HTML 안전성 검사

```bash
python3 -m unittest discover -s tests -v
python3 src/build.py
python3 -m http.server --directory _site 8766
```

생성한 HTML에 모든 링크를 포함하므로 JavaScript나 GitHub API 없이도 사이트 목록이 보인다. 방문자의 브라우저에서는 API를 호출하지 않는다. 검색·분류만 JavaScript로 작동한다. 외부 폰트·라이브러리·추적 스크립트는 사용하지 않는다.

루트 홈페이지와 기존 프로젝트 사이트는 별도 저장소로 배포된다. 메인 페이지를 수정해도 필드로봇·MarkTL·ICRA 등의 파일은 바뀌지 않는다.
