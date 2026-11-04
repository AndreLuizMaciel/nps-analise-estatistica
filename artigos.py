"""
Gera uma página própria para cada artigo do autor, com as etiquetas que o
Google Acadêmico lê (citation_*), além de sitemap.xml e robots.txt.

Uso: python artigos.py --saida _site   (rodar depois de publicacao.py)
Autor: André Luiz Maciel · ORCID 0009-0000-1747-1392 · Licença MIT
"""
import argparse, html, json, os, urllib.request

SITE = "https://andreluizmaciel.github.io/nps-analise-estatistica/"
AUTOR = "André Luiz Maciel"
AUTOR_CIT = "Maciel, André Luiz"
ORCID = "https://orcid.org/0009-0000-1747-1392"

ARTIGOS = [
    {
        "pasta": "nao-so-de-call-center",
        "titulo": "Não Só de Call Center Vive a Experiência do Cliente: qualidade estratégica, Voz do Cliente e análise de dados para transformar jornadas em resultados",
        "titulo_en": "It Takes More Than a Call Center to Deliver Customer Experience",
        "frase": "Não Só de Call Center Vive a Experiência do Cliente.",
        "data": "2026/04/28",
        "doi": "10.5281/zenodo.23898805",
        "pdf_nome": "nao-so-de-call-center-vive-a-experiencia-do-cliente-andre-luiz-maciel.pdf",
        "pdf_origem": "https://zenodo.org/records/23898805/files/nao-so-de-call-center-vive-a-experiencia-do-cliente-andre-luiz-maciel.pdf?download=1",
        "palavras": ["experiência do cliente", "Contact Center", "gestão da qualidade", "Net Promoter Score",
                     "Voz do Cliente", "melhoria contínua", "análise de dados", "jornada do cliente"],
        "resumo": "Este artigo argumenta que a experiência do cliente é resultado de uma jornada que envolve múltiplas áreas, e não apenas o desempenho do Contact Center. O Contact Center é tratado como sensor da organização, onde falhas de produto, processo, sistema e comunicação se tornam visíveis. O texto distingue três níveis de qualidade (da interação, da solução e da jornada) e discute os limites do Net Promoter Score como explicação isolada. Propõe um roteiro analítico de cinco perguntas, que separa ruído amostral de mudança real e efeito de mix de efeito de desempenho, e conecta o NPS a indicadores operacionais. Apresenta um modelo de governança transversal e um modelo integrado em sete etapas: capturar, contextualizar, validar, diagnosticar, priorizar, corrigir e verificar, e aprender. Conclui que a Qualidade atua como função integradora e alavanca estratégica de resultado.",
    },
    {
        "pasta": "qualidade-nao-e-controle",
        "titulo": "Qualidade não é controle. É alavanca estratégica de resultado: da monitoria à leitura estatística do NPS",
        "titulo_en": "Quality is not control. It is a strategic lever for results",
        "frase": "Qualidade não é controle. É alavanca estratégica de resultado.",
        "data": "2026/04/06",
        "doi": "10.5281/zenodo.23891605",
        "pdf_nome": None,
        "pdf_local": "artigo-qualidade-nao-e-controle-v2.pdf",
        "palavras": ["qualidade", "call center", "NPS", "estatística aplicada", "KPIs", "monitoria", "DMAIC"],
        "resumo": "O artigo propõe tratar a área de Qualidade de centrais de atendimento como alavanca estratégica de resultado, e não como função de controle. Apresenta a árvore de KPIs que liga SLA, TME, FCR, recontato, CES, TMA e CSAT ao NPS, os pilares de monitoria (Conhecimento, Operacional, Sistema, Processo e Atitude) e um roteiro estatístico para ler o NPS com rigor: margem de erro, teste de significância entre meses, carta de controle, decomposição mix × desempenho, regressão no nível da resposta e comparação justa entre atendentes. Os exemplos usam dados fictícios.",
    },
]


def baixar(url, destino):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "nps-analise-estatistica-build"})
        with urllib.request.urlopen(req, timeout=60) as r, open(destino, "wb") as f:
            f.write(r.read())
        return os.path.getsize(destino) > 1000
    except Exception as e:  # sem rede: a página aponta para o PDF no Zenodo
        print("aviso: não baixou", url, e)
        return False


def pagina(a, pdf_url):
    e = html.escape
    url = f"{SITE}{a['pasta']}/"
    metas = [("citation_title", a["titulo"]), ("citation_author", AUTOR_CIT),
             ("citation_author_orcid", ORCID), ("citation_publication_date", a["data"]),
             ("citation_publisher", "Zenodo"), ("citation_doi", a["doi"]),
             ("citation_pdf_url", pdf_url), ("citation_abstract_html_url", url),
             ("citation_language", "pt"), ("DC.creator", AUTOR), ("DC.title", a["titulo"]),
             ("DC.date", a["data"].replace("/", "-")), ("DC.identifier", "doi:" + a["doi"]),
             ("description", a["resumo"][:300]), ("author", AUTOR)]
    metas += [("citation_keywords", k) for k in a["palavras"]]
    meta_html = "\n".join(f'<meta name="{n}" content="{e(v)}">' for n, v in metas)
    ld = {"@context": "https://schema.org", "@type": "ScholarlyArticle", "headline": a["titulo"],
          "alternativeHeadline": a["titulo_en"], "datePublished": a["data"].replace("/", "-"),
          "inLanguage": "pt-BR", "license": "https://creativecommons.org/licenses/by/4.0/",
          "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": a["doi"]},
          "sameAs": "https://doi.org/" + a["doi"], "keywords": a["palavras"], "abstract": a["resumo"],
          "author": {"@type": "Person", "name": AUTOR, "sameAs": [ORCID,
                     "https://www.linkedin.com/in/andr%C3%A9-luiz-maciel-622a52119/",
                     "https://medium.com/@andreluizmaciel26", "https://github.com/AndreLuizMaciel"]}}
    ano = a["data"][:4]
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(a['titulo'])} | {AUTOR}</title>
{meta_html}
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{e(a['titulo'])}">
<meta property="og:description" content="{e(a['resumo'][:200])}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>body{{font-family:Georgia,serif;max-width:760px;margin:0 auto;padding:24px 16px;line-height:1.6;color:#1a2b3c;background:#fff}}
h1{{font-size:1.6rem;line-height:1.3}}blockquote{{border-left:4px solid #167d8d;margin:16px 0;padding:4px 16px;font-size:1.15rem}}
a{{color:#0f5f6b}}.meta{{color:#555;font-size:.95rem}}.box{{background:#eef5f6;padding:12px 16px;border-radius:8px}}</style>
</head><body>
<p class="meta">Artigo técnico · {ano} · Acesso aberto (CC BY 4.0)</p>
<h1>{e(a['titulo'])}</h1>
<p><b>{AUTOR}</b> · ORCID <a href="{ORCID}">0009-0000-1747-1392</a></p>
<blockquote>“{e(a['frase'])}” — {AUTOR}</blockquote>
<h2>Resumo</h2><p>{e(a['resumo'])}</p>
<p><b>Palavras-chave:</b> {e('; '.join(a['palavras']))}.</p>
<div class="box"><p><b>PDF completo:</b> <a href="{pdf_url}">{e(a['titulo'])}</a></p>
<p><b>DOI:</b> <a href="https://doi.org/{a['doi']}">{a['doi']}</a></p>
<p><b>Como citar:</b> MACIEL, André Luiz. {e(a['titulo'])}. Zenodo, {ano}. DOI: {a['doi']}.</p></div>
<p><a href="{SITE}">NPS com rigor estatístico: roteiro e código aberto</a> · <a href="{SITE}artigos/">Todos os artigos do autor</a></p>
</body></html>"""


def gerar(saida):
    urls = [SITE]
    itens = []
    for a in ARTIGOS:
        d = os.path.join(saida, a["pasta"]); os.makedirs(d, exist_ok=True)
        if a.get("pdf_local") and os.path.exists(os.path.join(saida, a["pdf_local"])):
            pdf_url = SITE + a["pdf_local"]
        elif a.get("pdf_nome") and baixar(a["pdf_origem"], os.path.join(d, a["pdf_nome"])):
            pdf_url = f"{SITE}{a['pasta']}/{a['pdf_nome']}"
        else:
            pdf_url = "https://doi.org/" + a["doi"]
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(pagina(a, pdf_url))
        urls.append(f"{SITE}{a['pasta']}/")
        itens.append(f'<li><a href="../{a["pasta"]}/">{html.escape(a["titulo"])}</a> ({a["data"][:4]}) · DOI <a href="https://doi.org/{a["doi"]}">{a["doi"]}</a></li>')
    d = os.path.join(saida, "artigos"); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Artigos de {AUTOR}</title><meta name="author" content="{AUTOR}"><meta name="description" content="Artigos técnicos de {AUTOR} sobre Qualidade, Customer Experience, Contact Center e NPS.">
<style>body{{font-family:Georgia,serif;max-width:760px;margin:0 auto;padding:24px 16px;line-height:1.6;color:#1a2b3c;background:#fff}}a{{color:#0f5f6b}}</style></head><body>
<h1>Artigos de {AUTOR}</h1><p>Qualidade · Customer Experience · Contact Center · NPS · ORCID <a href="{ORCID}">0009-0000-1747-1392</a></p>
<ul>{''.join(itens)}</ul></body></html>""")
    urls.append(SITE + "artigos/")
    with open(os.path.join(saida, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    with open(os.path.join(saida, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    print("Páginas de artigos geradas:", ", ".join(urls[1:]))
    # verificação do Google Search Console
    with open(os.path.join(saida, "google4ebf716b29e26e42.html"), "w", encoding="utf-8") as f:
        f.write("google-site-verification: google4ebf716b29e26e42.html")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--saida", default="_site")
    gerar(ap.parse_args().saida)
