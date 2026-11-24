#!/usr/bin/env python3
"""Generate the Portuguese version (pt/*.html) from the English pages.

The English pages are the source of truth. After editing them, run:
    python3 tools/make_pt.py
Paragraphs (bio, intros) are translated via the PARAGRAPHS table below; the
script stops with an error if an English paragraph has no translation, so
add/adjust the entry when the bio changes. List items are translated
automatically (titles stay in their original language).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "research.html", "policy.html", "media.html", "codes.html"]

NAV = {">Home<": ">Início<", ">Research<": ">Pesquisa<", ">Policy work<": ">Políticas públicas<",
       ">Media<": ">Mídia<", ">Codes<": ">Códigos<"}
HEADINGS = {
    "<h1>Research</h1>": "<h1>Pesquisa</h1>",
    "<h1>Policy work</h1>": "<h1>Políticas públicas</h1>",
    "<h1>Media</h1>": "<h1>Mídia</h1>",
    "<h1>Codes</h1>": "<h1>Códigos</h1>",
    "<h2>Published papers</h2>": "<h2>Artigos publicados</h2>",
    "<h2>Working papers</h2>": "<h2>Working papers</h2>",
    "<h2>MADE-USP Policy Notes (Notas de Política Econômica)</h2>": "<h2>Notas de Política Econômica (Made/USP)</h2>",
    "<h2>Policy reports</h2>": "<h2>Relatórios</h2>",
    "<h2>Public hearings</h2>": "<h2>Audiências públicas</h2>",
    "<h2>MADE Blog</h2>": "<h2>Blog do Made</h2>",
    "<h2>Op-eds and essays</h2>": "<h2>Artigos de opinião e ensaios</h2>",
    "<h2>Interviews and press coverage</h2>": "<h2>Entrevistas e imprensa</h2>",
}
TITLES = {"Research — ": "Pesquisa — ", "Policy work — ": "Políticas públicas — ",
          "Media — ": "Mídia — ", "Codes — ": "Códigos — "}
PARAGRAPHS = {
 "I am an economist interested in macroeconomics":
  "<p>Sou economista e me interesso por macroeconomia, desenvolvimento econômico e economia política. Atualmente sou professor de Economia na Universidade Federal do Rio de Janeiro (UFRJ) e coordenador de pesquisa em Macroeconomia no Centro de Pesquisa em Macroeconomia das Desigualdades (Made/USP). Sou doutor em Economia pela University of Massachusetts Amherst e livre-docente em Economia pela Universidade de São Paulo (FEA-USP). Antes de ingressar na UFRJ, fui professor de Economia na Universidade de Leeds, no Reino Unido.</p>",
 "My work has been published in journals such as":
  "<p>Meus trabalhos foram publicados em periódicos como <em>Journal of Development Economics</em>, <em>Oxford Bulletin of Economics and Statistics</em>, <em>Cambridge Journal of Economics</em>, <em>Industrial and Corporate Change</em> e <em>Review of Radical Political Economics</em>. Escrevi artigos de opinião para Project Syndicate, The Conversation, Phenomenal World, Aeon, Folha de S.Paulo, O Globo, O Estado de S. Paulo, Valor Econômico e Nexo, e dei entrevistas ou fui citado por <em>The Economist</em>, <em>Financial Times</em>, BBC Brasil, CNN Brasil e CNBC Brasil.</p>",
 "Policy notes, reports and short analyses":
  "<p>Notas, relatórios e análises curtas, em sua maioria produzidos no <a href=\"https://madeusp.com.br/\">Centro de Pesquisa em Macroeconomia das Desigualdades (Made/USP)</a>.</p>",
}
MONTHS = {"January": "janeiro", "February": "fevereiro", "March": "março", "April": "abril", "May": "maio",
          "June": "junho", "July": "julho", "August": "agosto", "September": "setembro", "October": "outubro",
          "November": "novembro", "December": "dezembro"}
META = [
    (r"\bWith ", "Com "), (r" and ", " e "), (r"\(online first\)", "(publicado online)"),
    (r"MADE-USP Working Paper", "Working Paper Made/USP"), (r"MADE Blog", "Blog do Made"),
    (r"^Interview\. ", "Entrevista. "), (r"^Quoted\. ", "Citado. "), (r"^Invited speaker\. ", "Expositor convidado. "),
    (r"Chamber of Deputies", "Câmara dos Deputados"), (r"Coverage of MADE research\. ", "Repercussão de pesquisa do Made. "),
    (r"London School of Economics", "London School of Economics"),
]
LINKS = {">Email<": ">E-mail<", ">CV<": ">Currículo<"}

def translate_meta(m):
    s = m.group(1)
    # keep <em>…</em> (journal names) untouched
    parts = re.split(r"(<em>.*?</em>)", s)
    out = []
    for p in parts:
        if p.startswith("<em>"):
            out.append(p); continue
        for a, b in META:
            p = re.sub(a, b, p)
        p = re.sub(r"\b(" + "|".join(MONTHS) + r") (\d{4})", lambda x: MONTHS[x.group(1)] + " de " + x.group(2), p)
        out.append(p)
    return '<span class="meta">' + "".join(out) + "</span>"

def toggle(html, href, label):
    return html.replace("</nav>", f'<a class="lang" href="{href}">{label}</a></nav>', 1)

def main():
    os.makedirs(os.path.join(ROOT, "pt"), exist_ok=True)
    missing = []
    for fn in PAGES:
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        # English page: make sure it has the PT toggle
        en = re.sub(r'<a class="lang"[^>]*>[^<]*</a>', "", src)
        en = toggle(en, f"pt/{fn}", "Português")
        if en != src:
            open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(en)
        pt = re.sub(r'<a class="lang"[^>]*>[^<]*</a>', "", src)
        pt = pt.replace('<html lang="en">', '<html lang="pt-BR">')
        pt = pt.replace('href="style.css', 'href="../style.css').replace('src="photo.jpg"', 'src="../photo.jpg"')
        pt = pt.replace('content="Guilherme Klein Martins, economist. Professor of Economics at UFRJ and researcher at MADE-USP."',
                        'content="Guilherme Klein Martins, economista. Professor de Economia da UFRJ e pesquisador do Made/USP."')
        for d in (NAV, HEADINGS, TITLES, LINKS):
            for a, b in d.items():
                pt = pt.replace(a, b)
        def para(m):
            text = m.group(0)
            for key, tr in PARAGRAPHS.items():
                if key in text:
                    return tr
            missing.append((fn, text[:90]))
            return text
        pt = re.sub(r"<p>.*?</p>", para, pt, flags=re.S)
        pt = re.sub(r'<span class="meta">(.*?)</span>', translate_meta, pt, flags=re.S)
        pt = toggle(pt, f"../{fn}", "English")
        open(os.path.join(ROOT, "pt", fn), "w", encoding="utf-8").write(pt)
    if missing:
        for fn, t in missing:
            print(f"UNTRANSLATED paragraph in {fn}: {t}…", file=sys.stderr)
        sys.exit(1)
    print("pt/ generated:", ", ".join(PAGES))

if __name__ == "__main__":
    main()
