from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
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
        self.id_counts: Counter[str] = Counter()
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
            self.id_counts[values["id"]] += 1
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
    duplicates = sorted(node_id for node_id, count in parser.id_counts.items() if count > 1)
    if duplicates:
        fail(f"{page.name} contains duplicate ids: {', '.join(duplicates)}")

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

index_parser = parsed[ROOT / "index.html"]
tabs = [attrs for _, attrs in index_parser.attrs if attrs.get("role") == "tab"]
panels = [attrs for _, attrs in index_parser.attrs if attrs.get("role") == "tabpanel"]
if len([tab for tab in tabs if "data-science-target" in tab]) != 6:
    fail("index.html must expose exactly six science tabs")
if len([tab for tab in tabs if "data-demo-target" in tab]) != 3:
    fail("index.html must expose exactly three product-demo tabs")
if sum(tab.get("aria-selected") == "true" for tab in tabs) != 2:
    fail("each tab interface must have one initially selected tab")
panel_ids = {panel.get("id") for panel in panels}
for tab in tabs:
    if not tab.get("id") or not tab.get("aria-controls"):
        fail("every tab needs an id and aria-controls")
    if tab["aria-controls"] not in panel_ids:
        fail(f"tab controls a missing panel: {tab['aria-controls']}")
for panel in panels:
    if panel.get("aria-labelledby") not in index_parser.ids:
        fail(f"panel has a missing aria-labelledby target: {panel.get('id')}")

index_text = (ROOT / "index.html").read_text(encoding="utf-8")
for required in (
    "Generation before automation",
    "Retrieval practice",
    "Practise future use",
    "Confidence before feedback",
    "Product inference: memory ≠ truth",
    "What the evidence does not say",
    "4,096-token context window",
):
    if required not in index_text:
        fail(f"index.html is missing required learning-science text: {required}")

support_text = (ROOT / "support.html").read_text(encoding="utf-8")
for required in (
    "Learning and review",
    "Find later",
    "Confidence before reveal",
    "Re-run evidence check",
):
    if required not in support_text:
        fail(f"support.html is missing required learning guidance: {required}")

privacy_text = (ROOT / "privacy.html").read_text(encoding="utf-8")
for required in (
    "on-device Foundation Model",
    "OpenAI live-web evidence",
    "OpenAI’s Responses API",
    "English Wikipedia",
    "Wikidata",
    "Crossref",
    "OpenAlex",
    "PubMed",
    "Europe PMC",
    "custom model endpoint",
    "Remote endpoints must use HTTPS",
    "pre-processing predictions",
    "confidence judgments",
    "GitHub Pages",
):
    if required not in privacy_text:
        fail(f"privacy.html is missing required boundary text: {required}")

print(f"Checked {len(PAGES)} pages: metadata, headings, ids, tab contracts, learning guidance, local links, fragments, and privacy boundaries passed.")
