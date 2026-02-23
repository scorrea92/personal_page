#!/usr/bin/env python3
"""Generate a static HTML section with the latest Medium posts from RSS.

- Fetches https://medium.com/feed/@<username>
- Extracts latest N items: title, link, pubDate, optional thumbnail
- Writes a HTML fragment to stdout (or a file if provided)

No external deps.
"""

import argparse
import html as htmllib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime


NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def first_img_url(html: str) -> str | None:
    if not html:
        return None
    m = re.search(r"<img[^>]+src=\"([^\"]+)\"", html)
    if m:
        return m.group(1)
    return None


def fmt_date(pub_date: str) -> str:
    # Medium uses RFC822-like: "Sun, 23 Feb 2026 12:34:56 GMT"
    try:
        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%b %Y")
    except Exception:
        return pub_date


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", default="scorrea92")
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()

    rss_url = f"https://medium.com/feed/@{args.username}"
    raw = fetch(rss_url)

    root = ET.fromstring(raw)
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else []

    posts = []
    for item in items[: args.count]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        content = item.findtext("content:encoded", default="", namespaces=NS)
        desc = item.findtext("description") or ""
        thumb = first_img_url(content) or first_img_url(desc)

        excerpt = strip_html(desc)
        if not excerpt:
            # Fallback: take first text from content:encoded
            excerpt = strip_html(content)
        # Medium content can be long; keep it tight
        if len(excerpt) > 180:
            excerpt = excerpt[:177].rstrip() + "…"
        posts.append({
            "title": title,
            "link": link,
            "date": fmt_date(pub),
            "thumb": thumb,
            "excerpt": excerpt,
        })

    # Build HTML fragment
    out = []
    out.append('')
    out.append('<!-- Medium Posts (auto-generated from RSS at build time). Do not edit by hand. -->')
    out.append('<section class="colorlib-blog" data-section="medium">')
    out.append('  <div class="colorlib-narrow-content">')
    out.append('    <div class="row">')
    out.append('      <div class="col-md-6 col-md-offset-3 col-md-pull-3 animate-box" data-animate-effect="fadeInLeft">')
    out.append('        <span class="heading-meta">Read</span>')
    out.append('        <h2 class="colorlib-heading">Medium Posts</h2>')
    out.append('      </div>')
    out.append('    </div>')
    out.append('    <div class="row">')

    for i, p in enumerate(posts):
        col_effect = "fadeInLeft" if i % 2 == 0 else "fadeInRight"
        title = htmllib.escape(p["title"])
        link = htmllib.escape(p["link"])
        date = htmllib.escape(p["date"])
        excerpt = htmllib.escape(p["excerpt"])
        thumb = p["thumb"]
        img_tag = (
            f'<img src="{htmllib.escape(thumb)}" class="img-responsive" alt="Medium post thumbnail">'
            if thumb
            else '<img src="images/blog-3.png" class="img-responsive" alt="Medium post">'
        )

        out.append(f'      <div class="col-md-4 col-sm-6 animate-box" data-animate-effect="{col_effect}">')
        out.append('        <div class="blog-entry">')
        out.append(f'          <a href="{link}" class="blog-img" target="_blank">{img_tag}</a>')
        out.append('          <div class="desc">')
        out.append(f'            <span><small>{date}</small> | <small>Medium</small></span>')
        out.append(f'            <h3><a href="{link}" target="_blank">{title}</a></h3>')
        out.append(f'            <p>{excerpt}</p>')
        out.append('          </div>')
        out.append('        </div>')
        out.append('      </div>')

    out.append('    </div>')
    out.append('    <div class="row" style="margin-top: 10px;">')
    out.append('      <div class="col-md-12">')
    out.append(f'        <p><a href="https://medium.com/@{htmllib.escape(args.username)}" target="_blank">See all posts on Medium →</a></p>')
    out.append('      </div>')
    out.append('    </div>')
    out.append('  </div>')
    out.append('</section>')

    frag = "\n".join(out) + "\n"

    if args.out == "-":
        sys.stdout.write(frag)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(frag)


if __name__ == "__main__":
    main()
