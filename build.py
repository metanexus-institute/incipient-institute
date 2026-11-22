#!/usr/bin/env python3
"""Build the static site and, optionally, its self-contained offline edition."""
import argparse
import base64
from datetime import date, datetime, timedelta
from html import escape
from itertools import groupby
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SITE_NAME = "Incipient Institute"
DEFAULT_ORIGIN = "https://example.org"
SOCIAL_IMAGE = "assets/social-card.jpg"
SOCIAL_IMAGE_ALT = "Incipient Institute wordmark and folded-square emblem beside the Pavilion at the edge of the woods."
HERO_SOURCES = (
    'srcset="assets/pavilion-compact.webp 640w, assets/pavilion-medium.webp 960w, assets/pavilion.webp 1536w" '
    'sizes="(max-width: 1320px) 90vw, 1232px"'
)
PAGES = {
    "index": ("Home", "An institute for an unfinished world", "Public programs, archived observations, and visitor records from the Incipient Institute, a research pavilion at the edge of the woods."),
    "about": ("About", "About the Institute", "The Incipient Institute's founding, senior fellows, and annual report on how people and places change through contact."),
    "programs": ("Programs", "Fellowships and Public Programs", "Read about resident fellowships, community field grants, and the Saturday Open Table at the Incipient Institute."),
    "visit": ("Visit", "Visit the Pavilion", "Read the Pavilion's published hours, arrival procedures, visitor agreement, and notices from the chair."),
    "pavilion": ("Pavilion Records", "Pavilion Records", "Facilities logs, floor plans, archived photographs, and revisions from the Incipient Pavilion."),
    "desk": ("Record desk", "Visitor Record Desk", "Request a copy of a Pavilion visitor record, compare it with the archive, and review replies from the east desk."),
}
NAVIGATION = ("about", "programs", "visit", "pavilion")
INDEXABLE = ("index", *NAVIGATION)


def canonical_origin(value):
    try:
        origin = urlsplit(value)
        valid_port = origin.port is None or 0 < origin.port <= 65535
    except ValueError:
        raise argparse.ArgumentTypeError("Enter an HTTPS site origin, such as https://example.org.") from None
    if (
        origin.scheme != "https"
        or not origin.hostname
        or origin.username is not None
        or origin.path not in ("", "/")
        or origin.query
        or origin.fragment
        or not valid_port
        or not re.fullmatch(r"[A-Za-z0-9.:[\]-]+", origin.netloc)
    ):
        raise argparse.ArgumentTypeError("Enter an HTTPS site origin, such as https://example.org.")
    return f"https://{origin.netloc.lower()}"


def page_url(page, origin):
    path = "" if page == "index" else f"{page}.html"
    return f"{origin}/{path}"


def page_title(page):
    subtitle = PAGES[page][1]
    return f"{SITE_NAME} | {subtitle}" if page == "index" else f"{subtitle} | {SITE_NAME}"


def metadata(page, origin):
    url = page_url(page, origin)
    name = page_title(page)
    description = PAGES[page][2]
    image = f"{origin}/{SOCIAL_IMAGE}"
    website = f"{origin}/#website"
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": website,
                "url": f"{origin}/",
                "name": SITE_NAME,
                "description": PAGES["index"][2],
                "genre": "Interactive fiction",
                "inLanguage": "en",
            },
            {
                "@type": "AboutPage" if page == "about" else "WebPage",
                "@id": url + "#webpage",
                "url": url,
                "name": name,
                "description": description,
                "isPartOf": {"@id": website},
                "inLanguage": "en",
            },
        ],
    }
    robots = "index,follow,max-image-preview:large" if page in INDEXABLE else "noindex,follow"
    fields = {
        "og:type": "website",
        "og:site_name": SITE_NAME,
        "og:locale": "en_US",
        "og:title": name,
        "og:description": description,
        "og:url": url,
        "og:image": image,
        "og:image:type": "image/jpeg",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": SOCIAL_IMAGE_ALT,
        "twitter:card": "summary_large_image",
        "twitter:title": name,
        "twitter:description": description,
        "twitter:image": image,
        "twitter:image:alt": SOCIAL_IMAGE_ALT,
    }
    tags = [
        f'<link rel="canonical" href="{escape(url)}">',
        '<link rel="describedby" href="/llms.txt" type="text/plain">',
        f'<meta name="robots" content="{robots}">',
    ]
    for key, value in fields.items():
        attribute = "property" if key.startswith("og:") else "name"
        tags.append(f'<meta {attribute}="{key}" content="{escape(value)}">')
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    tags.append(f'<script type="application/ld+json">{schema_text}</script>')
    return "\n  ".join(tags)


def write_discovery_files(origin):
    urls = "\n".join(f"  <url><loc>{escape(page_url(page, origin))}</loc></url>" for page in INDEXABLE)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {origin}/sitemap.xml\n", encoding="utf-8"
    )
    links = "\n".join(
        f"- [{PAGES[page][0]}]({page_url(page, origin)}): {PAGES[page][2]}" for page in INDEXABLE
    )
    (DIST / "llms.txt").write_text(
        f"# {SITE_NAME}\n\n"
        "> Interactive fiction told through the records, public programs, and visitor desk of a woodland research pavilion.\n\n"
        "The institute, personnel, visits, schedules, and archive records are elements of the fiction.\n\n"
        f"## Site pages\n\n{links}\n\n"
        "## Optional\n\n"
        f"- [Visitor Record Desk]({page_url('desk', origin)}): An interactive part of the story that keeps the visitor record in the browser.\n",
        encoding="utf-8",
    )


def navigation(current):
    return "".join(
        f'<a data-nav="{page}" href="{page}.html"'
        + (' aria-current="page"' if page == current else '')
        + f'>{PAGES[page][0]}</a>'
        for page in NAVIGATION
    )


def document(current, body, offline=False, origin=DEFAULT_ORIGIN):
    description = PAGES[current][2]
    discoverability = '<meta name="robots" content="noindex">' if offline else metadata(current, origin)
    home_href = "index.html" if offline else "./"
    body = body.replace(" data-hero-sources", "" if offline else f" {HERO_SOURCES}")
    css = (DIST / "styles.css").read_text() if offline else ""
    style = f'<style>{css}</style>' if offline else '<link rel="stylesheet" href="styles.css">'
    if offline:
        script = f'<script>{offline_router()}</script>\n<script>{(DIST / "desk.js").read_text()}</script>'
    else:
        script = '<script src="desk.js" defer></script>'
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f8f7f0">
  <meta name="description" content="{escape(description)}">
  <title>{escape(page_title(current))}</title>
  {discoverability}
  <link rel="icon" href="assets/mark-return.png" type="image/png">
  {style}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="masthead">
    <div class="frame masthead-inner">
      <a class="brand" href="{home_href}" aria-label="Incipient Institute, home">
        <img src="assets/mark-return.png" alt="" width="43" height="43">
        <span>Incipient<small>Institute</small></span>
      </a>
      <nav class="navigation" aria-label="Main navigation">{navigation(current)}</nav>
    </div>
  </header>
  <main id="main" tabindex="-1">
{body}
  </main>
  <footer class="site-footer">
    <div class="frame footer-inner">
      <div class="footer-identity">
        <a class="footer-mark" href="{home_href}" aria-label="Incipient Institute, home"><img src="assets/mark-return.png" alt="" width="36" height="36"></a>
        <p>© 2026 Incipient Institute</p>
        <p class="footer-credit">A Project of <a href="https://metanexus.net/">Metanexus Institute</a></p>
      </div>
      <nav aria-label="Footer navigation">
        <a href="visit.html">Visitor information</a>
        <a href="pavilion.html">Pavilion Records</a>
      </nav>
    </div>
  </footer>
{script}
</body>
</html>
'''


def offline_router():
    return """
const pages = [...document.querySelectorAll('[data-page]')];

function showPage(scroll) {
  const fragment = window.location.hash.slice(1);
  const target = document.getElementById(fragment);
  const current = target?.closest('[data-page]') ??
    (fragment === 'main' ? pages.find(page => !page.hidden) : pages[0]);
  for (const page of pages) page.hidden = page !== current;
  for (const link of document.querySelectorAll('[data-nav]')) {
    if (link.dataset.nav === current.dataset.page) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }
  document.title = current.dataset.title;
  if (!scroll) return;
  if (target && target !== current) {
    target.scrollIntoView();
    if (target.id !== 'main') target.setAttribute('tabindex', '-1');
    target.focus({ preventScroll: true });
  } else {
    window.scrollTo(0, 0);
    document.getElementById('main').focus({ preventScroll: true });
  }
}
window.addEventListener('hashchange', () => showPage(true));
showPage(Boolean(window.location.hash));
"""


def offline_edition(path, contents):
    blocks = []
    for page, content in contents.items():
        title = "Incipient Institute"
        if page != "index":
            title = page_title(page)
        blocks.append(f'    <div id="page-{page}" data-page="{page}" data-title="{escape(title)}">\n{content}\n    </div>')
    html = document("index", "\n".join(blocks), offline=True)

    def link(match):
        page, anchor = match.groups()
        return f'href="#{anchor or "page-" + page}"'

    def asset(match):
        source = DIST / match[0]
        mime = {"png": "png", "webp": "webp"}[source.suffix[1:]]
        return f"data:image/{mime};base64," + base64.b64encode(source.read_bytes()).decode("ascii")

    html = re.sub(r'href="([a-z]+)\.html(?:#([a-z-]+))?"', link, html)
    html = re.sub(r'assets/[a-z-]+\.(?:webp|png)', asset, html)
    path.write_text(html)


def log_period(entries):
    newest = entries[0][0].date()
    oldest = entries[-1][0].date()
    end = f"{newest.day} {newest:%B %Y}"
    if oldest == newest:
        return end
    if (oldest.year, oldest.month) == (newest.year, newest.month):
        return f"{oldest.day}–{end}"
    start = f"{oldest.day} {oldest:%B}"
    if oldest.year != newest.year:
        start += f" {oldest.year}"
    return f"{start}–{end}"


def facilities_archive(publication_date, parser):
    entries = []
    for line in (ROOT / "content" / "facilities-log.tsv").read_text().splitlines():
        timestamp, observation = line.split("\t", 1)
        entries.append((datetime.fromisoformat(timestamp), observation))

    times = [timestamp for timestamp, _ in entries]
    if not times or times != sorted(set(times)):
        parser.error("Facilities log entries need unique timestamps in ascending order.")
    if publication_date:
        cutoff = publication_date - timedelta(days=1)
        if times[-1].date() != cutoff:
            parser.error(f"Add a facilities log entry dated {cutoff} before publication.")

    archive = []
    weeks = groupby(reversed(entries), key=lambda entry: entry[0].isocalendar()[:2])
    for _, week in weeks:
        rows = list(week)
        period = log_period(rows)
        expanded = " open" if not archive else ""
        observations = "\n".join(
            f'                <tr><th scope="row"><time datetime="{stamp.isoformat(timespec="minutes")}">'
            f'{stamp.day} {stamp:%b · %H:%M}</time></th><td>{escape(note)}</td></tr>'
            for stamp, note in reversed(rows)
        )
        archive.append(f'''          <details class="disclosure log-period"{expanded}>
            <summary>{period}</summary>
            <table class="log">
              <caption class="visually-hidden">Facilities log, {period}</caption>
              <thead><tr><th scope="col">Entry</th><th scope="col">Observation</th></tr></thead>
              <tbody>
{observations}
              </tbody>
            </table>
          </details>''')
    return "\n".join(archive)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", type=Path)
    parser.add_argument("--publication-date", type=date.fromisoformat)
    parser.add_argument("--canonical-origin", type=canonical_origin, default=DEFAULT_ORIGIN)
    args = parser.parse_args()
    contents = {page: (ROOT / "content" / f"{page}.html").read_text() for page in PAGES}
    contents["pavilion"] = contents["pavilion"].replace(
        "          <!-- facilities-entries -->", facilities_archive(args.publication_date, parser)
    )
    for page, content in contents.items():
        (DIST / f"{page}.html").write_text(document(page, content, origin=args.canonical_origin))
    write_discovery_files(args.canonical_origin)
    if args.offline:
        offline_edition(args.offline, contents)


if __name__ == "__main__":
    main()
