# hanminy.github.io

[공개 메인 페이지](https://hanminy.github.io/) — 연구 자료, 개발·실험, 일상 사이트로 연결하는 정적 홈페이지.

## 분류

홈 화면의 카드는 종류에 따라 네 묶음으로 나눈다. `sites.json`의 `category`에 아래 이름 중 하나를 그대로 쓴다.

- **연구 아카이브**: 계속 갱신되는 사이트(대시보드, MarkTL, 스터디, 논문 뷰어)
- **발표**: 발표 슬라이드. 비공개 저장소 `hanminy-slides`에 있고 로그인해야 열린다.
- **설명 자료**: 혼자 읽어도 이해되는 완성된 페이지(이 저장소의 `assets/` 아래)
- **개인**: 여행 등 개인 자료

홈 화면은 이 네 묶음을 제목 달린 구역으로 나눠 보여 준다. 구역의 순서와 한 줄 설명은 `sites.json`의 `groups`에 적는다. 거기 없는 분류는 맨 뒤에 붙는다. 카드에 `"wide": true`를 주면 한 줄을 다 쓰고, `"tags"`는 카드 안의 작은 꼬리표로 나온다.

주제(굴착기, 피지컬 AI 등)로는 나누지 않는다. 묶음용 중간 페이지는 두지 않고 카드가 바로 자료를 가리킨다.

## 새 사이트 추가

- **새 공개 저장소의 GitHub Pages**: 다음 자동 배포에서 발견한다(매시간 17분). 분류를 정해 주지 않으면 `기타`로 뜨므로, `sites.json`의 `overrides`에 저장소 이름을 키로 `category`, `title`, `description`, `order`를 적는다.
- **이 저장소 안의 페이지나 다른 저장소의 하위 경로**: `extra_sites`에 고유 `id`, `title`, `description`, `url`, `category`, `label`, `order`를 추가한다.
- **제외할 저장소**: `exclude` 배열에 저장소 이름을 넣는다.
- **즉시 갱신**: Actions → Refresh site directory and deploy → Run workflow. 설정을 main에 push해도 배포한다.

GitHub Pages가 켜진 공개 저장소만 조회한다. 비공개 저장소, 일반 코드 저장소, 이 홈페이지 자체는 자동으로는 목록에 넣지 않는다. 새 사이트의 주소가 아직 404면 다음 실행에서 다시 확인한다. 기존에 설정한 주요 링크가 깨지거나 API 요청이 실패하면 배포를 중단하고 기존 공개본을 유지한다.

## 발표 자료는 여기에 올리지 않는다

발표 슬라이드, 작업 중간본, FES 자료실은 비공개 저장소 [hanminy-slides](https://github.com/hanminy/hanminy-slides)로 옮겼다. 그 저장소는 `https://hanminy-slides.pages.dev/`로 배포되고, 로그인한 사람만 볼 수 있다.

- 새 덱과 초안은 `hanminy-slides`에 올린다. 이 저장소의 `assets/`에 덱을 두면 누구나 볼 수 있게 된다. `tests/test_pages.py`가 옮긴 폴더가 다시 생기는지 검사한다.
- 홈 화면에는 "로그인 필요"로 표시된 카드가 그쪽을 가리킨다. 이런 사이트는 `sites.json`의 `extra_sites`에 `"private": true`로 적고, 주소의 호스트를 `private_hosts`에 넣는다. 로그인 화면으로 넘어가므로 배포 때 주소 확인은 하지 않는다.
- `assets/`에는 홈 화면용 파일과 공개로 두는 설명 자료(`bppv-guide/`, `inner-ear-imu/`)만 남긴다.

## 구조와 검증

- `sites.json`: 표시 이름과 하위 경로 설정
- `src/build.py`: 공개 저장소 발견, 주소 확인, HTML 생성 (Python 표준 라이브러리)
- `src/template.html`, `assets/`: 반응형 화면, 검색·분류
- `.github/workflows/pages.yml`: push·매시간·수동 갱신과 Pages 배포
- `tests/`: 새 사이트 자동 발견, 공개 범위, 로그인 필요 사이트, 하위 경로, 링크·HTML 안전성 검사

```bash
python3 -m unittest discover -s tests -v
python3 src/build.py
python3 -m http.server --directory _site 8766
```

생성한 HTML에 모든 링크를 포함하므로 JavaScript나 GitHub API 없이도 사이트 목록이 보인다. 방문자의 브라우저에서는 API를 호출하지 않는다. 검색·분류만 JavaScript로 작동한다. 외부 폰트·라이브러리·추적 스크립트는 사용하지 않는다.

루트 홈페이지와 기존 프로젝트 사이트는 별도 저장소로 배포된다. 메인 페이지를 수정해도 필드로봇·MarkTL·ICRA 등의 파일은 바뀌지 않는다.
