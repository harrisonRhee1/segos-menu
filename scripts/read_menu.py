"""uploads/ 폴더에 올라온 주간 메뉴표 사진을 Claude로 읽어 menu.json에 반영합니다.

GitHub Actions에서 실행되며, 저장소 Secrets의 ANTHROPIC_API_KEY를 사용합니다.
사용법: python scripts/read_menu.py <사진 경로> [<사진 경로> ...]
"""
import base64
import datetime as dt
import json
import mimetypes
import os
import sys
import urllib.request

MODEL = os.environ.get("MENU_MODEL", "claude-sonnet-5-5")
KST = dt.timezone(dt.timedelta(hours=9))
WD = "월화수목금토일"

PROMPT = """이 이미지는 한국 회사 구내식당의 주간 메뉴표입니다. 오늘 날짜는 {today} ({wd}요일)입니다.
표에 있는 날짜별 메뉴를 빠짐없이 읽어 주세요. 날짜에 연도가 없으면 오늘 날짜를 기준으로 가장 가까운 연도를 쓰세요.
날짜 대신 요일만 있으면 오늘이 속한 주(월~일)의 날짜로 바꾸세요.
식사 구분(조식/중식/석식 등)은 표에 적힌 이름을 그대로 쓰고, 메뉴 항목은 표에 적힌 순서대로 하나씩 별도 항목으로 나누세요.
칼로리가 있으면 숫자만 kcal에 넣으세요.
"*" 표시만 있거나 비어 있는 칸은 메뉴가 없는 것이므로 그 식사는 빼고, 메뉴가 하나도 없는 날은 days에 넣지 마세요.
중식 칸 바로 아래 이름 없는 한 줄(예: 요플레)은 그날 중식의 후식이니 중식 items 맨 끝에 넣으세요.
원산지 안내 같은 하단 설명은 무시하세요.
JSON만 답하세요. 형식:
{{"days":[{{"date":"2026-11-02","meals":[{{"name":"중식","items":["차조밥","바지락국","닭갈비"],"kcal":""}}]}}]}}"""


def ask_claude(path: str) -> list:
    key = os.environ["ANTHROPIC_API_KEY"]
    media = mimetypes.guess_type(path)[0] or "image/jpeg"
    if media not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        media = "image/jpeg"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    today = dt.datetime.now(KST).date()
    body = {
        "model": MODEL,
        "max_tokens": 4000,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}},
                {"type": "text", "text": PROMPT.format(today=today.isoformat(), wd=WD[today.weekday()])},
            ],
        }],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    text = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    start, end = text.find("{"), text.rfind("}")
    parsed = json.loads(text[start:end + 1])
    out = []
    for d in parsed.get("days", []):
        date = str(d.get("date", ""))
        try:
            dt.date.fromisoformat(date)
        except ValueError:
            continue
        meals = []
        for m in d.get("meals", []):
            items = [str(i).strip() for i in m.get("items", []) if str(i).strip() and str(i).strip() != "*"]
            if items:
                meals.append({"name": str(m.get("name") or "식사"), "items": items, **({"kcal": str(m["kcal"])} if m.get("kcal") else {})})
        if meals:
            out.append({"date": date, "meals": meals})
    return out


def main(paths: list) -> None:
    try:
        with open("menu.json", encoding="utf-8") as f:
            menu = json.load(f)
    except FileNotFoundError:
        menu = {"days": []}
    by_date = {d["date"]: d for d in menu.get("days", [])}
    total = 0
    for p in paths:
        days = ask_claude(p)
        print(f"{p}: {len(days)}일치 읽음 -> " + ", ".join(d["date"] for d in days))
        for d in days:
            by_date[d["date"]] = d
        total += len(days)
    if not total:
        sys.exit("사진에서 메뉴를 읽지 못했습니다. 더 선명한 사진으로 다시 올려 주세요.")
    cutoff = (dt.datetime.now(KST).date() - dt.timedelta(days=28)).isoformat()
    menu = {
        "updated": dt.datetime.now(KST).isoformat(timespec="minutes"),
        "days": sorted((d for d in by_date.values() if d["date"] >= cutoff), key=lambda d: d["date"]),
    }
    with open("menu.json", "w", encoding="utf-8") as f:
        json.dump(menu, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main([p for p in sys.argv[1:] if os.path.isfile(p)])
