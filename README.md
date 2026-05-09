# 섹터 스캐너 (코스피 · S&P 500)

`scanner.py` / `sp500_scanner.py`가 생성하는 `relay_universe.json`, `sp500_universe.json`을 보여 주는 로컬·모바일용 PWA입니다. 정적 파일만으로 동작하며 `pwa/index.html`을 브라우저에서 열면 됩니다.

## PWA (GitHub Pages)

저장소 루트에 `relay_universe.json`, `sp500_universe.json`, `pwa/`를 두고 `gh-pages` 브랜치 등으로 배포합니다. 예시 URL: `https://USERNAME.github.io/sector-scanner/pwa/index.html` (저장소 경로에 맞게 조정)

### 초기 업로드 (한 번)

```bat
cd /d "C:\Users\windows\Desktop\키움"
git init
git remote add origin https://github.com/USERNAME/sector-scanner.git
git checkout -b gh-pages
git add pwa/ relay_universe.json sp500_universe.json
git commit -m "init"
git push -u origin gh-pages
```

GitHub 저장소 **Settings → Pages**에서 Source: **Deploy from a branch**, Branch: **gh-pages** / **root** 를 선택합니다.

스캔 배치 마지막에 `auto_push.bat`이 호출되면 JSON만 스테이징·커밋·`gh-pages`로 push 합니다 (저장소·브랜치가 준비된 경우).

### 모바일 앱 설치 (안드로이드)

1. Chrome에서 아래 URL을 엽니다 (USERNAME·저장소명은 본인 것으로 바꿉니다).

   `https://USERNAME.github.io/sector-scanner/pwa/index.html`

2. Chrome 우측 상단 메뉴(⋮) → **홈 화면에 추가** 를 선택합니다.

3. **추가**를 누르면 홈 화면에 **섹터 스캐너** 아이콘이 생깁니다.

4. 첫 실행 후 상단 **⚙** 에서 데이터 베이스 URL을 입력합니다.

   `https://USERNAME.github.io/sector-scanner/`

   (끝에 슬래시 포함, JSON이 놓인 **저장소 루트** 기준)

이후 PC에서 스캔 배치가 돌고 `auto_push.bat`으로 JSON이 올라가면, 앱에서 **🔄** 로 최신 결과를 불러올 수 있습니다.

### 로컬 파일 모드

- `pwa/index.html`을 연 상태에서 `?source=local` 로 열면 베이스가 로컬(`./`)로 저장되고, **JSON은 상위 폴더**(`../relay_universe.json` 등)에서 읽습니다.
- `file://` 로 열면 fetch 제한으로 브라우저마다 동작이 다를 수 있습니다. 가능하면 로컬 정적 서버 또는 GitHub Pages를 사용하세요.
- Service Worker(오프라인 캐시)는 **HTTPS 또는 localhost**에서만 등록됩니다.
