# 섹터 스캐너 (코스피 · S&P 500)

`scanner.py` / `sp500_scanner.py`가 생성하는 `relay_universe.json`, `sp500_universe.json`을 보여 주는 로컬·모바일용 PWA입니다. 정적 파일만으로 동작하며 `pwa/index.html`을 브라우저에서 열면 됩니다.

## 텔레그램 알림 (피크 경고 · Grade A)

스캔 배치가 **성공한 뒤** 자동으로 `scanner_telegram_notify.py`가 실행됩니다.

- **조건**: `next_sectors.current_peak_risk` 이거나 **Grade A** 종목이 1개 이상일 때만 전송합니다.
- **중복 방지**: 피크 문구·Grade A 티커 목록이 직전 실행과 같으면 보내지 않습니다. (`scanner_telegram_notify_state.json`, git 제외)
- **강제 전송**: `py -3.12 scanner_telegram_notify.py --state-dir "..." --market kospi --force`

### 설정

1. `telegram_secrets.cmd.example` 을 복사해 **`telegram_secrets.cmd`** 로 두고, `TELEGRAM_BOT_TOKEN` · `TELEGRAM_CHAT_ID` 를 채웁니다. (이 파일은 `.gitignore`에 포함)
2. `run_sector_scanner_weekly.bat` / `run_sp500_scanner_weekly.bat` 는 스캔 성공 시 해당 파일이 있으면 `call` 한 뒤 알림 스크립트를 돌립니다.
3. 메시지 하단 PWA URL은 필요 시 환경변수 `SCANNER_PWA_URL` 로 덮어쓸 수 있습니다.

### 수동 테스트

```bat
py -3.12 scanner_telegram_notify.py --state-dir "C:\Users\windows\Desktop\키움" --market kospi --dry-run
```

## PWA (GitHub Pages)

저장소 루트에 `relay_universe.json`, `sp500_universe.json`, `pwa/`를 두고 `gh-pages` 브랜치 등으로 배포합니다. 배포 후 PWA 주소: [https://hahahan-bot.github.io/magic-scanner/pwa/index.html](https://hahahan-bot.github.io/magic-scanner/pwa/index.html)

### 초기 업로드 (한 번)

```bat
cd /d "C:\Users\windows\Desktop\키움"
git init
git remote add origin https://github.com/hahahan-bot/magic-scanner.git
git checkout -b gh-pages
git add pwa/ relay_universe.json sp500_universe.json
git commit -m "init"
git push -u origin gh-pages
```

GitHub 저장소 **Settings → Pages**에서 Source: **Deploy from a branch**, Branch: **gh-pages** / **root** 를 선택합니다.

스캔 배치 마지막에 `auto_push.bat`이 호출되면 JSON만 스테이징·커밋·`gh-pages`로 push 합니다 (저장소·브랜치가 준비된 경우).

### 모바일 앱 설치 (안드로이드)

1. Chrome에서 아래 URL을 엽니다.

   `https://hahahan-bot.github.io/magic-scanner/pwa/index.html`

2. Chrome 우측 상단 메뉴(⋮) → **홈 화면에 추가** 를 선택합니다.

3. **추가**를 누르면 홈 화면에 **섹터 스캐너** 아이콘이 생깁니다.

4. 첫 실행 후 상단 **⚙** 에서 데이터 베이스 URL을 입력합니다.

   `https://hahahan-bot.github.io/magic-scanner/`

   (끝에 슬래시 포함, JSON이 놓인 **저장소 루트** 기준)

이후 PC에서 스캔 배치가 돌고 `auto_push.bat`으로 JSON이 올라가면, 앱에서 **🔄** 로 최신 결과를 불러올 수 있습니다.

### 로컬 파일 모드

- `pwa/index.html`을 연 상태에서 `?source=local` 로 열면 베이스가 로컬(`./`)로 저장되고, **JSON은 상위 폴더**(`../relay_universe.json` 등)에서 읽습니다.
- `file://` 로 열면 fetch 제한으로 브라우저마다 동작이 다를 수 있습니다. 가능하면 로컬 정적 서버 또는 GitHub Pages를 사용하세요.
- Service Worker(오프라인 캐시)는 **HTTPS 또는 localhost**에서만 등록됩니다.
