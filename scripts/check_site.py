from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "index.html",
    ROOT / "support.html",
    ROOT / "privacy.html",
    ROOT / "client-rendered-source.html",
    ROOT / "404.html",
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.sources: list[str] = []
        self.h1_count = 0
        self.title_depth = 0
        self.title_text = ""

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attributes}
        self.attrs.append((tag, values))
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        if tag in {"img", "script", "link"} and values.get("src"):
            self.sources.append(values["src"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.title_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text += data


def fail(message: str) -> None:
    raise SystemExit(f"Site check failed: {message}")


missing = [page.name for page in PAGES if not page.is_file()]
if missing:
    fail(f"missing pages: {', '.join(missing)}")

parsed: dict[Path, PageParser] = {}
for page in PAGES:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8"))
    parsed[page] = parser

    html_nodes = [attrs for tag, attrs in parser.attrs if tag == "html"]
    if len(html_nodes) != 1 or html_nodes[0].get("lang") != "en":
        fail(f"{page.name} must declare exactly one html[lang=en]")
    if parser.h1_count != 1:
        fail(f"{page.name} must contain exactly one h1")
    if not parser.title_text.strip():
        fail(f"{page.name} must have a title")
    if not any(tag == "meta" and attrs.get("name") == "viewport" for tag, attrs in parser.attrs):
        fail(f"{page.name} is missing viewport metadata")
    if not any(tag == "meta" and attrs.get("name") == "description" and attrs.get("content") for tag, attrs in parser.attrs):
        fail(f"{page.name} is missing a description")
    if page.name != "404.html":
        if not any(tag == "link" and attrs.get("rel") == "canonical" for tag, attrs in parser.attrs):
            fail(f"{page.name} is missing a canonical URL")
        for property_name in ("og:type", "og:title", "og:description", "og:url"):
            if not any(tag == "meta" and attrs.get("property") == property_name and attrs.get("content") for tag, attrs in parser.attrs):
                fail(f"{page.name} is missing {property_name}")
    for tag, attrs in parser.attrs:
        if tag == "img" and "alt" not in attrs:
            fail(f"{page.name} has an image without an alt attribute")

for page, parser in parsed.items():
    for href in parser.hrefs:
        split = urlsplit(href)
        if split.scheme:
            if split.scheme != "https":
                fail(f"{page.name} uses a non-HTTPS external link: {href}")
            continue
        if href.startswith("//"):
            fail(f"{page.name} uses a scheme-relative link: {href}")
        target = page if not split.path else (page.parent / split.path).resolve()
        if not target.is_file():
            fail(f"{page.name} links to missing local file: {href}")
        if split.fragment:
            target_parser = parsed.get(target)
            if target_parser is None:
                target_parser = PageParser()
                target_parser.feed(target.read_text(encoding="utf-8"))
            if split.fragment not in target_parser.ids:
                fail(f"{page.name} links to missing fragment: {href}")

for required_asset in ("styles.css", "site.js", "brand-mark.svg", "app-icon.png"):
    if not (ROOT / required_asset).is_file():
        fail(f"required site asset is missing: {required_asset}")

for branded_page in (ROOT / "index.html", ROOT / "support.html", ROOT / "privacy.html"):
    if 'src="brand-mark.svg"' not in branded_page.read_text(encoding="utf-8"):
        fail(f"{branded_page.name} is not using the master product mark")

privacy_text = (ROOT / "privacy.html").read_text(encoding="utf-8")
for required in (
    "on-device Foundation Model",
    "LLM web research",
    "OpenAI’s Responses API",
    "English Wikipedia",
    "Crossref",
    "Europe PMC",
    "custom model endpoint",
    "Remote endpoints must use HTTPS",
    "GitHub Pages",
):
    if required not in privacy_text:
        fail(f"privacy.html is missing required boundary text: {required}")

print(f"Checked {len(PAGES)} pages: metadata, headings, image alternatives, local links, fragments, and privacy boundaries passed.")
