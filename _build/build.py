"""Build Chris Bartlett's website (https://bartlettcj.github.io) from one content list.

Run from anywhere:  python C:\\BartlettCJ.github.io\\_build\\build.py

What it does
- Reads the record data fetched from DataCite (`datacite_meta.json`, beside this file) for titles,
  subtitles and abstracts, so the site says exactly what the Zenodo records say.
- Copies each paper's PDF from its local source into the site under a STABLE file name. Stable
  names matter: Google Scholar remembers the PDF address, and a name that changes with every version
  breaks it. Replace the bytes, keep the name.
- Writes every page: home, the three section pages (AI, Science & Medicine, Other), one page per
  paper edition (with the hidden citation_* tags Google Scholar reads), sitemap.xml, robots.txt
  and 404.html.

To add a new work: add it to WORKS below (and its record to datacite_meta.json if it has a DOI),
run this script, preview, commit. Publishing (git push) is the owner's call: see README.md.

Folders starting with "_" are not published by GitHub Pages, so this script and its data stay in the
repository without appearing on the site.
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # the site folder (repository root)
META = json.loads((Path(__file__).parent / "datacite_meta.json").read_text(encoding="utf-8"))

SITE = {
    "name": "Chris Bartlett",
    "url": "https://bartlettcj.github.io",
    "orcid": "0009-0001-3323-0131",
    "substack": "https://substack.com/@asihopeium",
    "links": [
        ("ORCID", "https://orcid.org/0009-0001-3323-0131"),
        ("Substack", "https://substack.com/@asihopeium"),
        ("X", "https://x.com/BartlettChrisJ"),
        ("LinkedIn", "https://www.linkedin.com/in/bartlettchris/"),
        ("GitHub", "https://github.com/BartlettCJ"),
    ],
}

# Home page introduction: the owner's own wording (his "Website text" doc, 2026-10-09), with spelling
# and grammar corrected and each correction reported to him. Change only on his say-so.
INTRO = [
    "I'm a developer and specialist in applied AI. I'm also an independent researcher, futurist and "
    "writer. I write about artificial intelligence, science and medicine, and sometimes issues of "
    "philosophy and cosmology.",
    "I started my career in pharmaceuticals and biotechnology, eventually editing a national consumer "
    "health and medical magazine.",
    "Raised in the UK near Oxford, I graduated in Biology and Psychology from Oxford Brookes University "
    "and now live permanently in Japan.",
]

# Contact page text: the owner's own wording, moved here from the home page (2026-10-09).
CONTACT_TEXT = [
    "Anyone is welcome to freely contact me about my work, though I may not always be able to answer "
    "immediately. Let me know if you need an urgent reply.",
    "I also consult independently as a futurist, and as an AI specialist in particular. If you think I "
    "can help you or your business, please contact me. There is no fee for the initial consultation, of course.",
]

# Optional settings kept on this computer only (not in the repository).
_LOCAL = Path(__file__).parent / "local_settings.json"
LOCAL_SETTINGS = json.loads(_LOCAL.read_text(encoding="utf-8")) if _LOCAL.exists() else {}
CONTACT = LOCAL_SETTINGS.get("contact", "")

# What Google shows under the site's name in search results (the home page's meta description).
HOME_DESCRIPTION = ("Chris Bartlett: applied AI specialist, developer, independent researcher, futurist "
                    "and writer on AI, science and medicine, philosophy and cosmology.")

SECTIONS = [
    ("ai", "AI", "ai.html", "Essays and papers on artificial intelligence."),
    ("science", "Science & Medicine", "science.html", "Reviews and evidence synthesis in biology and medicine."),
    ("other", "Other", "other.html", "Other projects and interests."),
]

# Tabs along the top of every page: the sections, then Contact.
NAV = [(label, fname) for _sid, label, fname, _blurb in SECTIONS] + [("Contact", "contact.html")]

# Extra lines under a section's description (HTML).
SECTION_EXTRA = {
    "ai": 'More of my writing on AI is on my Substack, <a href="https://substack.com/@asihopeium">ASI Hopeium</a>.',
}

LANG_NAMES = {
    "en": "English", "ja": "日本語", "zh-Hans": "简体中文", "zh-Hant": "繁體中文", "ko": "한국어",
    "es": "Español", "ru": "Русский", "it": "Italiano", "pt-BR": "Português (Brasil)",
    "pt-PT": "Português (Portugal)", "fr": "Français", "de": "Deutsch", "ca": "Català",
}

PROM1_SRC = Path(r"C:\PROM1\manuscript\2026-09-18-v0.6\publication\zenodo")
PROM1_EDITIONS = [
    # (language, record key in datacite_meta.json, sub-folder, local PDF)
    ("en", "prom1-en", "", PROM1_SRC / "deposit_en_v1.90" / "PROM1_REVIEW_v1.90.pdf"),
    ("ja", "prom1-ja", "ja", PROM1_SRC / "deposit_ja_v1.90" / "PROM1_REVIEW_v1.90_JA.pdf"),
    ("zh-Hans", "prom1-zh-hans", "zh-hans", PROM1_SRC / "deposit_zh_v1.90" / "PROM1_REVIEW_v1.90_ZH_CN.pdf"),
    ("zh-Hant", "prom1-zh-hant", "zh-hant", PROM1_SRC / "deposit_hant_v1.90" / "PROM1_REVIEW_v1.90_ZH_HANT.pdf"),
    ("ko", "prom1-ko", "ko", PROM1_SRC / "deposit_ko_v1.90" / "PROM1_REVIEW_v1.90_KO.pdf"),
    ("es", "prom1-es", "es", PROM1_SRC / "deposit_es_v1.90" / "PROM1_REVIEW_v1.90_ES.pdf"),
    ("ru", "prom1-ru", "ru", PROM1_SRC / "deposit_ru_v1.90" / "PROM1_REVIEW_v1.90_RU.pdf"),
    ("it", "prom1-it", "it", PROM1_SRC / "deposit_it_v1.90" / "PROM1_REVIEW_v1.90_Italiano.pdf"),
    ("pt-BR", "prom1-pt-br", "pt-br", PROM1_SRC / "deposit_pt_br_v1.90" / "PROM1_REVIEW_v1.90_PT_BR.pdf"),
    ("pt-PT", "prom1-pt-pt", "pt-pt", PROM1_SRC / "deposit_pt_pt_v1.90" / "PROM1_REVIEW_v1.90_PT_PT.pdf"),
    ("fr", "prom1-fr", "fr", PROM1_SRC / "deposit_fr_v1.90" / "PROM1_REVIEW_v1.90_Francais.pdf"),
]

# Papers and essays that get their own pages (and their PDF hosted here).
WORKS = [
    {
        "id": "data-in-motion",
        "section": "ai",
        "kind": "Essay",
        "path": "papers/data-in-motion/",
        "editions": [{
            "lang": "en", "key": "asi", "dir": "",
            "pdf_src": Path(r"C:\ASIHopeium\data_in_motion\published\Bartlett_2024_Humanity_data_in_motion_published_2026-09-20.pdf"),
            "pdf_name": "humanity-data-in-motion.pdf",
            "date": "2024-05-13",
            "date_line": "First published on ASI Hopeium, 13\u00a0May\u00a02024. Repository edition, 20\u00a0September\u00a02026.",
            "date_line_html": 'First published on <a href="https://substack.com/@asihopeium">ASI Hopeium</a>, '
                              "13\u00a0May\u00a02024. Repository edition, 20\u00a0September\u00a02026.",
            "licence": ("CC BY-NC-ND 4.0", "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
            "cite": "Bartlett C. Humanity represents unique and priceless data in motion. ASI Hopeium, "
                    "13 May 2024. Repository edition, Zenodo, 20 September 2026.",
        }],
    },
    {
        "id": "prom1",
        "section": "science",
        "kind": "Review",
        "path": "papers/prom1/",
        "note": "The Zenodo record also holds an accessible HTML edition, a spoken-text version, a "
                "description of the figure and an audiobook.",
        "editions": [
            {
                "lang": lang, "key": key, "dir": sub, "pdf_src": src,
                "pdf_name": "prom1-retinal-degeneration" + ("" if lang == "en" else "-" + sub) + ".pdf",
                "date": "2026-09-21",
                "date_line": "Working paper, version 1.90, 21\u00a0September\u00a02026.",
                "licence": ("CC BY-NC 4.0", "https://creativecommons.org/licenses/by-nc/4.0/"),
                "cite": None,  # built from the edition's own title below
            }
            for lang, key, sub, src in PROM1_EDITIONS
        ],
    },
]

# Order of the cards under "Recent work" on the home page (owner, 2026-10-09: PROM1 first).
RECENT_ORDER = ["prom1", "data-in-motion"]

# Books: listed on their section page only (no PDF hosted here; the books are on sale).
BOOKS = [
    {
        "section": "other",
        "title": "Courtly Love: Lancelot of the Lake – The Tale of the Cart",
        # HTML allowed here (it is written by hand, not taken from a record).
        "summary_html": (
            "The first complete English translation of Gaston Paris's 1883 article on Lancelot and the "
            'Tale of the Cart (<cite>Romania</cite> 12, <span class="nowrap">459–534</span>), the article '
            "in which the expression <i lang=\"fr\">amour courtois</i> gained its currency. Translated and "
            "edited by C.J. Bartlett, with all 185 of Paris's notes and, in the paperback, the original "
            "French on facing pages."
        ),
        # Paperbacks only (owner, 2026-10-09). Each checked on Amazon.com that day by its ISBN.
        "editions": [
            ("en", "Courtly Love: Lancelot of the Lake – The Tale of the Cart", "979-8-1748-3268-8"),
            ("ja", "宮廷風恋愛: 湖のランスロ 荷車の物語", "979-8-1752-8571-1"),
            ("es", "Amor cortés: Lanzarote del Lago – El cuento de la carreta", "979-8-1768-1106-3"),
            ("ca", "Amor cortès: Lancelot del Llac – El conte de la carreta", "979-8-1768-0995-4"),
            ("de", "Höfische Liebe: Lancelot vom See – Die Erzählung vom Karren", "979-8-1786-1175-3"),
            ("it", "Amore cortese: Lancillotto del Lago – Il racconto della carretta", "979-8-1786-1789-2"),
        ],
    },
]

E = html.escape


def meta_for(key):
    rec = META[key]
    titles = [t for t in rec["titles"] if not t.get("titleType")]
    subtitle = next((t["title"] for t in rec["titles"] if t.get("titleType") == "Subtitle"), "")
    translated = next((t["title"] for t in rec["titles"] if t.get("titleType") == "TranslatedTitle"), "")
    abstract = next((d["description"] for d in rec["descriptions"] if d.get("descriptionType") == "Abstract"), "")
    return {
        "doi": rec["doi"],
        # ASCII hyphen in titles: easier to search for than the U+2010 hyphen in the records.
        "title": titles[0]["title"].replace("\u2010", "-"),
        "subtitle": subtitle.replace("\u2010", "-"),
        "translated": translated.replace("\u2010", "-"),
        "abstract": abstract,
        "keywords": rec.get("subjects") or [],
    }


def gene_italic(text):
    """Italicise the gene symbol PROM1 in a title, as the paper does."""
    return E(text).replace("PROM1", "<em>PROM1</em>")


def rel(depth):
    return "../" * depth


def page(title, body, depth, lang="en", head_extra="", description="", canonical=""):
    nav = "".join(f'<a href="{rel(depth)}{f}">{E(label)}</a>' for label, f in NAV)
    links = " · ".join(f'<a href="{u}" rel="me">{E(n)}</a>' for n, u in SITE["links"])
    canon = f'<link rel="canonical" href="{E(canonical)}">' if canonical else ""
    desc = f'<meta name="description" content="{E(description)}">' if description else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
{desc}
{canon}
<link rel="stylesheet" href="{rel(depth)}css/site.css">
{head_extra}
</head>
<body>
<a class="skip" href="#main" lang="en">Skip to content</a>
<header class="site" lang="en">
  <a class="brand" href="{rel(depth)}index.html">{E(SITE['name'])}</a>
  <nav aria-label="Sections">{nav}</nav>
</header>
<main id="main">
{body}
</main>
<footer class="site" lang="en">
  <p>{links}</p>
</footer>
</body>
</html>
"""


def edition_url(work, ed):
    return SITE["url"] + "/" + work["path"] + (ed["dir"] + "/" if ed["dir"] else "")


def edition_cite(work, ed, m):
    if ed["cite"]:
        return ed["cite"]
    title = m["title"]
    if m["subtitle"]:
        sep = "：" if ed["lang"] in ("ja", "zh-Hans", "zh-Hant") else ": "
        title = f"{title}{sep}{m['subtitle'][0].lower() + m['subtitle'][1:] if ed['lang'] == 'en' else m['subtitle']}"
    return f"Bartlett C. {title}. Version 1.90. Zenodo, 21 September 2026."


def build_edition_page(work, ed):
    m = meta_for(ed["key"])
    out_dir = ROOT / work["path"] / ed["dir"] if ed["dir"] else ROOT / work["path"]
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ed["pdf_src"], out_dir / ed["pdf_name"])
    depth = work["path"].count("/") + (1 if ed["dir"] else 0)
    url = edition_url(work, ed)
    pdf_url = url + ed["pdf_name"]
    y, mo, d = ed["date"].split("-")

    tags = [
        ("citation_title", m["title"]),
        ("citation_author", "Bartlett, Chris"),
        ("citation_publication_date", f"{y}/{mo}/{d}"),
        ("citation_pdf_url", pdf_url),
        ("citation_abstract_html_url", url),
        ("citation_doi", m["doi"]),
        ("citation_language", ed["lang"]),
    ] + [("citation_keywords", k.replace("\u2010", "-")) for k in m["keywords"]]
    head = "\n".join(f'<meta name="{n}" content="{E(v)}">' for n, v in tags)

    # Language alternates: every edition of this work points at every other.
    if len(work["editions"]) > 1:
        head += "\n" + "\n".join(
            f'<link rel="alternate" hreflang="{o["lang"]}" href="{E(edition_url(work, o))}">'
            for o in work["editions"]
        )
        head += f'\n<link rel="alternate" hreflang="x-default" href="{E(edition_url(work, work["editions"][0]))}">'

    ld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "name": m["title"],
        "headline": m["title"],
        "inLanguage": ed["lang"],
        "datePublished": ed["date"],
        "author": {"@type": "Person", "name": "Chris Bartlett",
                   "sameAs": [u for _n, u in SITE["links"]]},
        "identifier": "https://doi.org/" + m["doi"],
        "sameAs": "https://doi.org/" + m["doi"],
        "url": url,
        "encoding": {"@type": "MediaObject", "contentUrl": pdf_url, "encodingFormat": "application/pdf"},
        "license": ed["licence"][1],
    }
    if m["subtitle"]:
        ld["alternativeHeadline"] = m["subtitle"]
    if ed["lang"] != "en" and len(work["editions"]) > 1:
        ld["translationOfWork"] = {"@type": "ScholarlyArticle", "url": edition_url(work, work["editions"][0])}
    head += f'\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'

    others = ""
    if len(work["editions"]) > 1:
        items = "".join(
            f'<li{" aria-current=\"page\"" if o is ed else ""}><a href="{rel(depth)}{work["path"]}{o["dir"] + "/" if o["dir"] else ""}" '
            f'lang="{o["lang"]}">{E(LANG_NAMES[o["lang"]])}</a></li>'
            for o in work["editions"]
        )
        others = f'<section class="editions" lang="en"><h2>Read in</h2><ul class="langs">{items}</ul></section>'

    eng_title = ""
    if ed["lang"] != "en" and m["translated"]:
        eng_title = f'<p class="engtitle" lang="en">English title: {gene_italic(m["translated"])}</p>'
    note = f'<p class="note" lang="en">{E(work["note"])}</p>' if work.get("note") else ""
    cite = edition_cite(work, ed, m)
    doi_link = f'<a href="https://doi.org/{m["doi"]}">https://doi.org/{m["doi"]}</a>'
    # Two columns on wide screens: the text on the left, the buttons, licence and languages on the
    # right. On a phone the right column comes first, so the PDF button is at the top.
    body = f"""<article class="paper">
<header class="paper-head">
<p class="kind" lang="en">{E(work['kind'])}</p>
<h1>{gene_italic(m['title'])}</h1>
{f'<p class="subtitle">{gene_italic(m["subtitle"])}</p>' if m['subtitle'] else ''}
{eng_title}
<p class="byline" lang="en">Chris Bartlett · <a href="https://orcid.org/{SITE['orcid']}">ORCID {SITE['orcid']}</a></p>
<p class="dateline" lang="en">{ed.get('date_line_html') or E(ed['date_line'])}</p>
</header>
<div class="paper-body">
<div class="paper-main">
{note}
<h2 lang="en">Abstract</h2>
<p class="abstract">{E(m['abstract'])}</p>
<h2 lang="en">How to cite</h2>
<p class="cite">{gene_italic(cite)} {doi_link}</p>
</div>
<aside class="paper-side" lang="en">
<p class="actions"><a class="button" href="{E(ed['pdf_name'])}">Read the PDF</a> <a class="button secondary" href="https://doi.org/{m['doi']}">Zenodo record</a></p>
<p class="licence">Licence: <a href="{ed['licence'][1]}">{E(ed['licence'][0])}</a></p>
{others}
</aside>
</div>
</article>"""
    title = f"{m['title']} | {SITE['name']}"
    (out_dir / "index.html").write_text(
        page(title, body, depth, lang=ed["lang"], head_extra=head,
             description=m["abstract"][:300], canonical=url),
        encoding="utf-8",
    )
    return url


def work_card(work, depth=0):
    en = work["editions"][0]
    m = meta_for(en["key"])
    teaser = m["abstract"].split(". ")[0].rstrip(".") + "."
    langs = ""
    if len(work["editions"]) > 1:
        langs = '<p class="langs-inline">Also in ' + ", ".join(
            f'<a href="{rel(depth)}{work["path"]}{o["dir"]}/" lang="{o["lang"]}">{E(LANG_NAMES[o["lang"]])}</a>'
            for o in work["editions"][1:]
        ) + "</p>"
    return f"""<article class="card">
<p class="kind">{E(work['kind'])}</p>
<h3><a href="{rel(depth)}{work['path']}">{gene_italic(m['title'])}</a></h3>
{f'<p class="subtitle">{gene_italic(m["subtitle"])}</p>' if m['subtitle'] else ''}
<p class="dateline">{en.get('date_line_html') or E(en['date_line'])}</p>
<p>{E(teaser)}</p>
{langs}
</article>"""


def book_card(book):
    rows = []
    for lang, title, isbn in book["editions"]:
        rows.append(
            f'<li><span lang="{lang}">{E(title)}</span> <span class="meta">({E(LANG_NAMES[lang])}: '
            f'paperback, ISBN <a class="nowrap" href="https://www.amazon.com/s?k={isbn.replace("-", "")}">'
            f"{isbn}</a>)</span></li>"
        )
    return f"""<article class="card">
<p class="kind">Book</p>
<h3>{E(book['title'])}</h3>
<p>{book['summary_html']}</p>
<ul class="books">{''.join(rows)}</ul>
<p class="meta">On sale on every Amazon store.</p>
</article>"""


def build():
    built = []
    for work in WORKS:
        for ed in work["editions"]:
            built.append(build_edition_page(work, ed))

    for sid, label, fname, blurb in SECTIONS:
        cards = [work_card(w) for w in WORKS if w["section"] == sid]
        cards += [book_card(b) for b in BOOKS if b["section"] == sid]
        extra = f'<p class="lede">{SECTION_EXTRA[sid]}</p>\n' if sid in SECTION_EXTRA else ""
        body = (f'<h1>{E(label)}</h1>\n<p class="lede">{E(blurb)}</p>\n{extra}'
                f'<div class="cards">\n' + "\n".join(cards) + "\n</div>")
        (ROOT / fname).write_text(
            page(f"{label} | {SITE['name']}", body, 0, description=blurb,
                 canonical=f"{SITE['url']}/{fname}"),
            encoding="utf-8",
        )
        built.append(f"{SITE['url']}/{fname}")

    person = {
        "@context": "https://schema.org", "@type": "Person", "name": "Chris Bartlett",
        "alternateName": "C.J. Bartlett", "url": SITE["url"] + "/",
        "sameAs": [u for _n, u in SITE["links"]],
    }
    by_id = {w["id"]: w for w in WORKS}
    latest = "\n".join(work_card(by_id[i]) for i in RECENT_ORDER)
    # The introduction, with a small ORCID box beside it on wide screens (owner, 2026-10-09).
    id_box = (
        f'<aside class="id-box"><p class="kind">ORCID</p>'
        f'<p><a href="https://orcid.org/{SITE["orcid"]}">{SITE["orcid"]}</a></p>'
        f'<p class="kind">Substack</p>'
        f'<p><a href="{SITE["substack"]}">ASI Hopeium</a></p></aside>'
    )
    body = (
        '<div class="intro-row">\n<section class="intro">' + "".join(f"<p>{E(p)}</p>" for p in INTRO)
        + f"</section>\n{id_box}\n</div>\n"
        f'<section><h2>Recent work</h2>\n<div class="cards">\n{latest}\n</div>\n</section>'
    )
    (ROOT / "index.html").write_text(
        page(SITE["name"], body, 0,
             head_extra=f'<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>',
             description=HOME_DESCRIPTION,
             canonical=SITE["url"] + "/"),
        encoding="utf-8",
    )
    built.insert(0, SITE["url"] + "/")

    # Contact page: the owner's text, then the email button at the bottom right.
    button = ""
    if CONTACT:
        v = ",".join(str(ord(c) + 7) for c in CONTACT)
        button = (
            f'<p class="contact-button"><button type="button" class="button secondary reveal" data-v="{v}">'
            "Show my email address</button></p>\n"
            "<script>document.querySelectorAll('.reveal').forEach(function (b) {"
            "b.addEventListener('click', function () {"
            "var s = String.fromCharCode.apply(null, b.dataset.v.split(',').map(function (n) { return n - 7; }));"
            "var a = document.createElement('a'); a.href = 'mail' + 'to:' + s; a.textContent = s;"
            "b.replaceWith(a); a.focus(); });});</script>"
        )
    body = '<h1>Contact</h1>\n<section class="contact-text">' + "".join(f"<p>{E(p)}</p>" for p in CONTACT_TEXT) + "</section>\n" + button
    (ROOT / "contact.html").write_text(
        page(f"Contact | {SITE['name']}", body, 0, description=CONTACT_TEXT[0],
             canonical=f"{SITE['url']}/contact.html"),
        encoding="utf-8",
    )
    built.append(f"{SITE['url']}/contact.html")

    (ROOT / "404.html").write_text(
        page(f"Page not found | {SITE['name']}", '<h1>Page not found</h1><p><a href="/">Go to the home page</a>.</p>', 0),
        encoding="utf-8",
    )
    sitemap = "".join(f"<url><loc>{E(u)}</loc></url>" for u in built)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n',
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")
    check_no_plain_emails()
    print(f"built {len(built)} pages into {ROOT}")


def check_no_plain_emails():
    """Owner's rule (2026-10-09): no email address in plain text on any page. The PDFs may carry one."""
    import re
    pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    hits = []
    for path in ROOT.rglob("*"):
        if path.suffix.lower() in (".html", ".xml", ".txt", ".css", ".js") and "_build" not in path.parts:
            for m in pattern.finditer(path.read_text(encoding="utf-8", errors="replace")):
                hits.append(f"{path.relative_to(ROOT)}: {m.group(0)}")
    if hits:
        raise SystemExit("Plain-text email address on the site, refusing to finish:\n  " + "\n  ".join(hits))


if __name__ == "__main__":
    build()
