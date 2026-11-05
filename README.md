# 세고스 구내식당 메뉴표

휴대폰 홈 화면 아이콘 한 번으로 오늘·주간 메뉴를 보는 웹앱입니다. 앱스토어 심사 없이 GitHub Pages(무료)로 운영합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| `index.html` | 메뉴 화면 (오늘의 메뉴 / 주간 메뉴) |
| `menu.json` | 메뉴 데이터. 화면은 이 파일만 읽습니다 |
| `uploads/` | 관리자가 메뉴표 사진을 올리는 폴더 |
| `scripts/read_menu.py` | 사진을 Claude로 읽어 `menu.json`을 고치는 프로그램 |
| `.github/workflows/read-menu.yml` | 사진이 올라오면 위 프로그램을 자동 실행 |
| `manifest.webmanifest`, `sw.js`, `icon-*.png` | 홈 화면 아이콘, 오프라인 보기 |

## 처음 한 번만 설정

1. **저장소 만들기**: GitHub에서 새 저장소(예: `segos-menu`)를 **Public**으로 만들고 이 폴더의 파일을 모두 올립니다. 무료 계정은 Public 저장소만 Pages를 쓸 수 있습니다.
2. **Pages 켜기**: 저장소 → Settings → Pages → Source를 `Deploy from a branch`, Branch를 `main` / `/(root)`로 저장합니다. 1~2분 뒤 `https://<아이디>.github.io/segos-menu/` 주소가 생깁니다.
3. **사진 자동 읽기 켜기**: https://console.anthropic.com 에서 API 키를 발급받고, 저장소 → Settings → Secrets and variables → Actions → New repository secret에 이름 `ANTHROPIC_API_KEY`로 저장합니다. 사진 한 장 읽는 비용은 수십 원 수준입니다.

## 매주 메뉴 올리기 (관리자)

1. GitHub 앱 또는 웹에서 저장소의 `uploads` 폴더로 들어갑니다.
2. Add file → Upload files로 메뉴표 사진을 올리고 Commit 합니다. 파일 이름은 자유입니다(예: `2026-11-09.png`).
3. 1~3분 뒤 Actions 탭의 "메뉴표 사진 읽기"가 끝나면 `menu.json`이 갱신되고, 직원 화면에 반영됩니다.
4. 읽은 내용이 틀렸으면 `menu.json`을 열어 연필 아이콘으로 직접 고치면 됩니다.

## 직원 안내 문구 (사내 공지용)

> 구내식당 메뉴를 휴대폰에서 바로 볼 수 있습니다.
> 아래 주소를 열고 홈 화면에 추가해 주세요.
> - 아이폰: Safari로 열기 → 공유 버튼 → "홈 화면에 추가"
> - 갤럭시: Chrome으로 열기 → 오른쪽 위 ⋮ → "홈 화면에 추가"
>
> 주소: https://<아이디>.github.io/segos-menu/

## 참고

- Public 저장소이므로 주소를 아는 사람은 누구나 메뉴를 볼 수 있습니다. 메뉴 외의 사내 정보는 이 저장소에 올리지 마세요.
- 메뉴표 사진은 `uploads` 폴더에 남습니다. 오래된 사진은 지워도 화면에는 영향이 없습니다.
- `menu.json`에는 최근 4주치만 남고 그보다 오래된 날짜는 자동으로 정리됩니다.
