"""인스타 최신 게시물 12개 → assets/ig_feed/ 이미지 + feed.json."""
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v21.0"
IG_USER_ID = "17841471697854191"  # 오쏘핏 공식 인스타 계정
ROOT = pathlib.Path(__file__).parent
IMG_DIR = ROOT / "assets" / "ig_feed"
LIMIT = 12
FIELDS = "id,media_type,media_url,thumbnail_url,permalink,caption"


def get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Meta가 돌려주는 상세 에러(code/subcode/message)를 로그에 남김
        print(f"HTTP {e.code} 에러 응답: {e.read().decode(errors='replace')}")
        raise


def pick_image_url(m):
    """릴스(VIDEO)는 썸네일, 이미지/캐러셀은 media_url."""
    return m.get("thumbnail_url") if m.get("media_type") == "VIDEO" else m.get("media_url")


def download(url, dest):
    tmp = dest.with_suffix(".tmp")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        tmp.write_bytes(r.read())
    tmp.replace(dest)


def main():
    token = os.environ["IG_ACCESS_TOKEN"]

    q = urllib.parse.urlencode({"fields": FIELDS, "limit": LIMIT, "access_token": token})
    media = get_json(f"{API}/{IG_USER_ID}/media?{q}")["data"]

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for m in media:
        url = pick_image_url(m)
        if not url:
            continue
        dest = IMG_DIR / f"{m['id']}.jpg"
        if not dest.exists():
            download(url, dest)  # 실패하면 예외 → 워크플로우 실패, 기존 피드 유지
        items.append({
            "image": f"assets/ig_feed/{m['id']}.jpg",
            "permalink": m["permalink"],
            "caption": m.get("caption", ""),
            "media_type": m["media_type"],
        })
        if len(items) == LIMIT:
            break

    if not items:
        raise SystemExit("가져온 게시물이 없어 중단")

    keep = {pathlib.Path(i["image"]).name for i in items}
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in keep:
            f.unlink()

    # 타임스탬프를 넣지 않아야 변경이 있을 때만 커밋됨
    (ROOT / "feed.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"feed.json 생성: {len(items)}개")


if __name__ == "__main__":
    main()
