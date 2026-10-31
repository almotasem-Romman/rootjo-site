"""Publish approved Root posts to Instagram (and the Facebook Page) through the official Graph API.

posts/<id>/post.json : {"status": "approved", "caption": "...", "image": "image.jpg", "targets": ["instagram", "facebook"]}
posts/<id>/image.jpg : JPEG, 1080x1440 (3:4) or 1080x1350 (4:5)
After publishing, posts/<id>/published.json is written with the post ids and links.
A push with no approved posts only checks that the token works and prints the connected accounts.
"""
import json, os, sys, time, urllib.parse, urllib.request, glob

TOKEN = os.environ.get("META_TOKEN", "")
V = os.environ.get("GRAPH_VERSION", "v23.0")
RAW = os.environ.get("RAW_BASE", "")
G = f"https://graph.facebook.com/{V}"


def call(method, path, **params):
    params["access_token"] = params.get("access_token", TOKEN)
    data = urllib.parse.urlencode(params).encode()
    url = f"{G}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise SystemExit(f"Graph API error on {method} {path}: {msg}")


def accounts():
    pages = call("GET", "me/accounts", fields="id,name,access_token,instagram_business_account{id,username}").get("data", [])
    if not pages:
        raise SystemExit("The token sees no Facebook Page. Assign the RootComputers Page to the system user and add pages_show_list.")
    page = pages[0]
    ig = page.get("instagram_business_account") or {}
    if not ig.get("id"):
        raise SystemExit(f"Page {page['name']} has no linked Instagram business account visible to this token.")
    return page, ig


def ig_publish(ig_id, image_url, caption):
    c = call("POST", f"{ig_id}/media", image_url=image_url, caption=caption)
    cid = c["id"]
    for _ in range(30):
        s = call("GET", cid, fields="status_code,status").get("status_code")
        if s == "FINISHED":
            break
        if s in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Instagram could not process the image (status {s}).")
        time.sleep(4)
    p = call("POST", f"{ig_id}/media_publish", creation_id=cid)
    link = call("GET", p["id"], fields="permalink").get("permalink", "")
    return {"id": p["id"], "permalink": link}


def fb_publish(page, image_url, caption):
    r = call("POST", f"{page['id']}/photos", url=image_url, message=caption, access_token=page["access_token"])
    pid = r.get("post_id") or r.get("id")
    return {"id": pid, "permalink": f"https://www.facebook.com/{pid}"}


def main():
    if not TOKEN:
        raise SystemExit("META_TOKEN secret is missing. Add it in GitHub: Settings > Secrets and variables > Actions.")
    page, ig = accounts()
    print(f"Token OK. Facebook Page: {page['name']} ({page['id']}) | Instagram: @{ig.get('username')} ({ig['id']})")
    todo = []
    for f in sorted(glob.glob("posts/*/post.json")):
        d = os.path.dirname(f)
        if os.path.exists(os.path.join(d, "published.json")):
            continue
        post = json.load(open(f, encoding="utf-8"))
        if post.get("status") == "approved":
            todo.append((d, post))
    if not todo:
        print("No approved posts waiting. Nothing published.")
        return
    for d, post in todo:
        url = f"{RAW}/{d}/{post.get('image', 'image.jpg')}"
        targets = post.get("targets", ["instagram", "facebook"])
        out = {"published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        print(f"Publishing {d} -> {targets}")
        if "instagram" in targets:
            out["instagram"] = ig_publish(ig["id"], url, post["caption"])
            print("  Instagram:", out["instagram"]["permalink"])
        if "facebook" in targets:
            out["facebook"] = fb_publish(page, url, post["caption"])
            print("  Facebook:", out["facebook"]["permalink"])
        json.dump(out, open(os.path.join(d, "published.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
