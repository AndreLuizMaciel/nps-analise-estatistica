"""
Gera a publicação (site estático) a partir da base fictícia.
Uso: python publicacao.py --saida _site

Autor: André Luiz Maciel · Licença: MIT (código) / CC BY 4.0 (texto)
"""
from __future__ import annotations

import argparse
import html
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import dados_sinteticos as ds
import nps_toolkit as nt

AZUL, VERDE, CINZA, VERMELHO = "#1f5f8b", "#2a9d6f", "#8a94a0", "#c2453d"
FATORES = ["lento_24h", "evento_sazonal", "reclamacao", "canal_email", "recontato_7d"]
ROTULOS = {"lento_24h": "Resolvido após 24h", "evento_sazonal": "Evento sazonal",
           "reclamacao": "Reclamação", "canal_email": "Pesquisa por e-mail", "recontato_7d": "Recontato em 7 dias"}
REPO = "https://github.com/AndreLuizMaciel/nps-analise-estatistica"
URL = "https://andreluizmaciel.github.io/nps-analise-estatistica/"


def _estilo(ax, titulo):
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold", color="#1b1f24")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.text(1, -0.16, "Dados fictícios · nps_toolkit", transform=ax.transAxes, ha="right", fontsize=8, color=CINZA)


def graficos(df, pasta):
    os.makedirs(pasta, exist_ok=True)
    mensal = nt.limites_controle(nt.nps_por(df, "mes"))

    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(len(mensal))
    ax.fill_between(x, mensal["lic"], mensal["lsc"], color=AZUL, alpha=0.08, label="Limites de controle (3σ)")
    ax.axhline(mensal["centro"].iloc[0], color=CINZA, lw=1, ls="--", label="NPS do período")
    ax.errorbar(x, mensal["nps"], yerr=mensal["margem95"], fmt="o-", color=AZUL, capsize=4, label="NPS do mês ± margem 95%")
    ax.set_xticks(x, mensal["mes"])
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    _estilo(ax, "NPS mensal com margem de erro e carta de controle")
    fig.tight_layout(); fig.savefig(f"{pasta}/01_nps_mensal.png", dpi=150); plt.close(fig)

    faixa = nt.nps_por(df, "faixa_resolucao")
    fig, ax = plt.subplots(figsize=(9, 4))
    cores = [VERDE if i < 3 else VERMELHO for i in range(len(faixa))]
    ax.bar(faixa["faixa_resolucao"].astype(str), faixa["nps"], yerr=faixa["margem95"], color=cores, capsize=4)
    _estilo(ax, "NPS por tempo de resolução")
    fig.tight_layout(); fig.savefig(f"{pasta}/02_nps_tempo.png", dpi=150); plt.close(fig)

    meses = sorted(df["mes"].unique())
    mix, des = [], []
    for a, b in zip(meses[:-1], meses[1:]):
        d = nt.decomposicao_mix(df, "mes", "faixa_resolucao", a, b).loc["TOTAL"]
        mix.append(d["mix"]); des.append(d["desempenho"])
    fig, ax = plt.subplots(figsize=(9, 4.2))
    xs = np.arange(len(mix))
    ax.bar(xs - 0.2, mix, width=0.4, color=CINZA, label="Mix (composição dos casos)")
    ax.bar(xs + 0.2, des, width=0.4, color=AZUL, label="Desempenho (mesmo caso, nota diferente)")
    ax.plot(xs, np.array(mix) + np.array(des), "D", color="#1b1f24", ms=5, label="Variação total")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(xs, [f"{b}" for b in meses[1:]])
    ax.legend(frameon=False, fontsize=8)
    _estilo(ax, "Variação mês contra mês: mix × desempenho")
    fig.tight_layout(); fig.savefig(f"{pasta}/03_shift_share.png", dpi=150); plt.close(fig)

    mod = nt.modelo_resposta(df, FATORES)
    m = mod.loc[FATORES].sort_values("coef")
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh([ROTULOS[i] for i in m.index], m["coef"], xerr=nt.Z95 * m["erro_padrao"], color=VERMELHO, capsize=4)
    ax.axvline(0, color="#333", lw=0.8)
    ax.grid(axis="x", alpha=0.25)
    _estilo(ax, "Quantos pontos de NPS cada fator tira de uma resposta")
    fig.tight_layout(); fig.savefig(f"{pasta}/04_modelo.png", dpi=150); plt.close(fig)

    at = nt.dispersao_atendentes(df)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    o = at.sort_values("n")
    ax.plot(o["n"], o["funil_sup"], color=CINZA, lw=1); ax.plot(o["n"], o["funil_inf"], color=CINZA, lw=1)
    fora = (at["nps"] > at["funil_sup"]) | (at["nps"] < at["funil_inf"])
    ax.scatter(at["n"], at["nps"], c=np.where(fora, VERMELHO, AZUL), s=30, zorder=3)
    ax.axhline(nt.resumo_nps(df["nota"])["nps"], color=CINZA, ls="--", lw=1)
    ax.set_xlabel("Respostas do atendente"); ax.set_ylabel("NPS")
    _estilo(ax, "Gráfico de funil: quem está de fato fora do esperado")
    fig.tight_layout(); fig.savefig(f"{pasta}/05_funil_atendentes.png", dpi=150); plt.close(fig)
    return mensal, faixa, mod, at


def tabela_html(df_, colunas, formatos):
    th = "".join(f"<th>{html.escape(c)}</th>" for c in colunas.values())
    linhas = []
    for _, r in df_.iterrows():
        tds = "".join(f"<td>{'–' if isinstance(r[k], float) and np.isnan(r[k]) else formatos.get(k, '{}').format(r[k])}</td>" for k in colunas)
        linhas.append(f"<tr>{tds}</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(linhas)}</tbody></table>"


def gerar_site(saida):
    df = ds.gerar()
    mensal, faixa, mod, at = graficos(df, f"{saida}/img")
    teste = nt.teste_mes_a_mes(nt.nps_por(df, "mes"))
    geral = nt.resumo_nps(df["nota"])
    sig = teste[teste["significativo_95"]]
    meses_sig = ", ".join(sig["mes"]) or "nenhum mês"
    maior = teste["delta"].abs().idxmax()
    cf = nt.nps_sem_segmento(df[df["mes"].between("M05", "M07")], df[df["mes"].between("M05", "M07")]["evento_sazonal"] == 1)
    cen_lento = nt.simular_cenario(df, mod, {"lento_24h": df["lento_24h"].mean() / 2})
    cen_tudo = nt.simular_cenario(df, mod, {"lento_24h": 0})
    temas = nt.marcar_temas(df.loc[df["nota"] <= 6, "comentario"].replace("", np.nan).dropna(), {
        "Retorno e prazo": r"demor|esper|prazo|retorno|dias",
        "Sistema e acesso": r"aplicativo|app|site|acess|codigo|entrar",
        "Resposta genérica": r"generic|robo|pronta|metade|nao leram",
        "Regra e elegibilidade": r"regra|direito|motivo",
    })
    tem = temas.mean().mul(100).sort_values(ascending=False).round(0)
    elegiveis = at[at["elegivel"]]

    tab_mes = tabela_html(teste, {"mes": "Mês", "n": "Respostas", "nps": "NPS", "margem95": "Margem 95% (±)",
                                  "delta": "Δ vs mês anterior", "p_valor": "p-valor"},
                          {"n": "{:.0f}", "nps": "{:.1f}", "margem95": "{:.1f}", "delta": "{:+.1f}", "p_valor": "{:.2f}"})
    tab_mod = tabela_html(mod.reset_index().rename(columns={"index": "fator"}).assign(
        fator=lambda d: d["fator"].map(lambda f: ROTULOS.get(f, f))),
        {"fator": "Fator", "coef": "Pontos de NPS", "erro_padrao": "Erro-padrão", "t": "t"},
        {"coef": "{:+.1f}", "erro_padrao": "{:.1f}", "t": "{:.1f}"})
    tab_tema = "".join(f"<li><b>{html.escape(k.replace('sem_tema', 'Sem tema identificado'))}</b>: {v:.0f}% dos comentários</li>" for k, v in tem.items())

    pagina = PAGINA.format(
        url=URL, repo=REPO, n=len(df), nps=geral["nps"], margem=geral["margem95"],
        meses_sig=meses_sig, maior_mes=teste.loc[maior, "mes"], maior_delta=teste.loc[maior, "delta"],
        maior_p=teste.loc[maior, "p_valor"], tab_mes=tab_mes, tab_mod=tab_mod,
        nps_rapido=faixa.iloc[:3]["nps"].mean(), nps_lento=faixa.iloc[3:]["nps"].mean(),
        cf_total=cf["nps_total"], cf_sem=cf["nps_sem_grupo"], cf_grupo=cf["nps_do_grupo"],
        cf_peso=cf["peso_grupo_%"], cf_detr=cf["parcela_detratores_%"],
        base=mod.iloc[0]["coef"], cen_lento=cen_lento, cen_tudo=cen_tudo,
        at_min=elegiveis["nps"].min(), at_max=elegiveis["nps"].max(),
        at_min_aj=elegiveis["nps_ajustado"].min(), at_max_aj=elegiveis["nps_ajustado"].max(),
        temas=tab_tema,
    )
    with open(f"{saida}/index.html", "w", encoding="utf-8") as f:
        f.write(pagina)
    df.to_csv(f"{saida}/base_ficticia.csv", index=False)
    print(f"Site gerado em {saida}/ ({len(df)} respostas fictícias)")


PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NPS com rigor estatístico: ruído, mudança real e o que move o indicador | André Luiz Maciel</title>
<meta name="description" content="Publicação de André Luiz Maciel: como ler o NPS de uma central de atendimento com margem de erro, teste de significância, decomposição mix × desempenho, regressão no nível da resposta e gráfico de funil. Com código aberto em Python.">
<meta name="author" content="André Luiz Maciel">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="NPS com rigor estatístico — André Luiz Maciel">
<meta property="og:description" content="Framework aberto para separar ruído de mudança real no NPS e encontrar o que move o indicador.">
<meta property="og:image" content="{url}img/01_nps_mensal.png">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"TechArticle","headline":"NPS com rigor estatístico: ruído, mudança real e o que move o indicador",
"author":{{"@type":"Person","name":"André Luiz Maciel","alternateName":"Andre Luiz Maciel de Lima Silva",
"jobTitle":"Coordenador de Qualidade · CX · Analytics","sameAs":["https://www.linkedin.com/in/andr%C3%A9-luiz-maciel-622a52119/","https://medium.com/@andreluizmaciel26","https://github.com/AndreLuizMaciel","https://doi.org/10.5281/zenodo.23891606"]}},
"inLanguage":"pt-BR","url":"{url}","codeRepository":"{repo}","license":"https://creativecommons.org/licenses/by/4.0/",
"keywords":"NPS, Net Promoter Score, margem de erro, teste z, shift-share, regressão, call center, qualidade, customer experience"}}
</script>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']]}}}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>
<style>
:root{{--ink:#1b1f24;--muted:#5b6470;--line:#dfe3e8;--soft:#f4f7f9;--accent:#1f5f8b;--bg:#fff}}
@media (prefers-color-scheme:dark){{:root{{--ink:#e7ebef;--muted:#a3adb8;--line:#2c333b;--soft:#161b21;--accent:#7cb7e0;--bg:#0e1216}} img{{background:#fff;border-radius:6px}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:760px;margin:0 auto;padding:48px 16px 80px}}
.k{{color:var(--accent);font-weight:700;font-size:13px;letter-spacing:.06em;text-transform:uppercase}}
h1{{font-size:clamp(28px,5vw,40px);line-height:1.15;margin:8px 0 12px}} h2{{font-size:23px;margin:44px 0 8px}}
.by{{color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:16px}}
img{{width:100%;height:auto;margin:12px 0}} table{{width:100%;border-collapse:collapse;font-size:14px;margin:12px 0}}
.tw{{overflow-x:auto}} th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:right}} th:first-child,td:first-child{{text-align:left}}
pre{{background:var(--soft);padding:14px;border-radius:8px;overflow-x:auto;font-size:14px}} code{{font-size:.92em}}
.box{{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin:24px 0}}
.aviso{{border-left:4px solid var(--accent)}} a{{color:var(--accent)}}
</style>
</head>
<body><main><article>
<div class="k">Publicação técnica · Qualidade, CX e Estatística</div>
<h1>NPS com rigor estatístico: como separar ruído de mudança real e descobrir o que move o indicador</h1>
<p class="by">Por <b>André Luiz Maciel</b> · Coordenador de Qualidade, especialista em CX e análise de dados · Código aberto em <a href="{repo}">GitHub</a></p>

<div class="box aviso"><b>Sobre os dados.</b> Todos os números e gráficos desta página vêm de uma base <b>fictícia</b> com {n:,} respostas, gerada pelo script <code>dados_sinteticos.py</code>. O objetivo é mostrar o <b>método</b>; nenhum dado de empresa real é usado.</div>

<p>Toda central de atendimento conhece a cena: o NPS do mês cai três pontos e a reunião vira uma caça ao culpado. No mês seguinte sobe quatro e ninguém sabe dizer por quê. O problema raramente é o atendimento; é a <b>leitura</b> do indicador. Esta publicação reúne, de forma aplicada, o roteiro estatístico que uso para responder três perguntas antes de qualquer plano de ação:</p>
<ol><li><b>A variação é real ou é ruído de amostra?</b></li><li><b>Ela veio de mudança no tipo de caso ou de piora no mesmo tipo de caso?</b></li><li><b>Quais fatores tiram mais pontos e quanto valeria corrigir cada um?</b></li></ol>
<p>É a aplicação prática de uma ideia que defendo: <i>“Qualidade não é controle. É alavanca estratégica de resultado.”</i> A Qualidade só vira alavanca quando lê os números com método.</p>

<h2>1. O NPS é uma média e isso muda tudo</h2>
<p>Dê a cada resposta o valor +100 (promotor, notas 9–10), 0 (neutro, 7–8) ou −100 (detrator, 0–6). A média desse vetor é exatamente o NPS. Como é uma média, ela tem variância e, portanto, margem de erro:</p>
<p>\\(\\mathrm{{NPS}} = 100\\,(p_+ - p_-) \\qquad \\mathrm{{var}} = p_+ + p_- - (p_+ - p_-)^2 \\qquad \\text{{margem}}_{{95\\%}} = 1{{,}}96\\,\\sqrt{{\\mathrm{{var}}/n}}\\times 100\\)</p>
<p>Na base fictícia, o NPS do período é <b>{nps:.1f}</b> com margem de <b>±{margem:.1f}</b> pontos. Em um único mês, com 200 a 400 respostas, a margem passa facilmente de ±8 pontos. Ou seja: boa parte do “sobe e desce” cabe dentro do ruído.</p>

<h2>2. Ruído ou mudança real? Teste mês contra mês e carta de controle</h2>
<p>Para comparar dois meses, use o teste z da diferença de duas médias independentes:</p>
<p>\\(z = \\dfrac{{\\mathrm{{NPS}}_2-\\mathrm{{NPS}}_1}}{{100\\sqrt{{\\mathrm{{var}}_1/n_1+\\mathrm{{var}}_2/n_2}}}}\\)</p>
<img src="img/01_nps_mensal.png" alt="NPS mensal com margem de erro e limites de controle — dados fictícios">
<div class="tw">{tab_mes}</div>
<p>Na base fictícia, a maior variação foi em <b>{maior_mes}</b> ({maior_delta:+.1f} pts, p = {maior_p:.2f}); variações com significância a 95%: <b>{meses_sig}</b>. A carta de controle (linha central = NPS do período, limites de ±3σ ajustados ao n de cada mês) complementa o teste: ela mostra se o processo saiu do padrão, e não só se dois meses diferem.</p>
<p><b>Regra prática:</b> antes de explicar uma variação, mostre a margem de erro dela. Comparar <i>blocos</i> de meses (trimestre contra trimestre) aumenta o n e revela mudanças de patamar que o mês a mês esconde.</p>

<h2>3. O fator que mais explica o mês: tempo de resolução</h2>
<img src="img/02_nps_tempo.png" alt="NPS por faixa de tempo de resolução — dados fictícios">
<p>Casos resolvidos em até 24h têm NPS médio de <b>{nps_rapido:.0f}</b>; acima de 24h, <b>{nps_lento:.0f}</b>. Quando a fatia de casos lentos oscila, o NPS do mês oscila junto, mesmo que o atendimento “bom” continue igual. Esse é o tipo de achado que tira a discussão do campo da opinião.</p>

<h2>4. Mix × desempenho: a decomposição shift-share</h2>
<p>Uma queda pode vir de duas fontes: (a) chegaram mais casos de um tipo que naturalmente avalia pior (<b>mix</b>) ou (b) o mesmo tipo de caso passou a ser avaliado pior (<b>desempenho</b>). A decomposição separa as duas de forma exata:</p>
<p>\\(\\Delta\\mathrm{{NPS}} = \\underbrace{{\\textstyle\\sum_g (w_{{g,1}}-w_{{g,0}})\\,\\mathrm{{NPS}}_{{g,0}}}}_{{\\text{{mix}}}} + \\underbrace{{\\textstyle\\sum_g w_{{g,1}}\\,(\\mathrm{{NPS}}_{{g,1}}-\\mathrm{{NPS}}_{{g,0}})}}_{{\\text{{desempenho}}}}\\)</p>
<img src="img/03_shift_share.png" alt="Decomposição mix × desempenho mês a mês — dados fictícios">
<p>Mix pede ação de <b>gestão de demanda e prazo</b> (fila, priorização, WFM). Desempenho pede ação de <b>tratativa</b> (calibração, script, conhecimento). Confundir os dois é o erro mais caro da gestão de NPS.</p>

<h2>5. Contrafactual: quanto um grupo de casos pesa no resultado</h2>
<p>Pergunta simples e poderosa: qual seria o NPS sem um grupo específico de casos? Nos meses M05–M07 da base fictícia, um “evento sazonal” representou <b>{cf_peso:.0f}%</b> das respostas, com NPS de <b>{cf_grupo:.0f}</b>, e respondeu por <b>{cf_detr:.0f}%</b> dos detratores. Sem ele, o NPS do trimestre seria <b>{cf_sem:.1f}</b> em vez de <b>{cf_total:.1f}</b>. Isso mostra onde a causa está, muitas vezes fora da central: regra, comunicação ou prazo do produto.</p>

<h2>6. Modelo no nível da resposta: o peso de cada fator</h2>
<p>Uma regressão linear com \\(y \\in \\{{+100, 0, -100\\}}\\) e fatores 0/1 tem uma leitura direta: cada coeficiente é <b>quantos pontos de NPS</b> aquele fator tira de uma resposta, mantidos os demais. O intercepto é o NPS esperado do caso-base. Uso erros-padrão robustos (HC1), porque y tem só três valores.</p>
<img src="img/04_modelo.png" alt="Coeficientes do modelo em pontos de NPS — dados fictícios">
<div class="tw">{tab_mod}</div>
<p>Com o modelo, os cenários viram conta: reduzir pela metade os casos resolvidos após 24h levaria o NPS fictício de {nps:.1f} para <b>{cen_lento:.1f}</b>; zerar atraso levaria a <b>{cen_tudo:.1f}</b>. O caso-base (sem nenhum fator negativo) teria <b>{base:.1f}</b>. Isso responde à pergunta da diretoria: “o que precisa acontecer para batermos a meta?”</p>

<h2>7. Atendentes: dispersão sem ranking injusto</h2>
<p>Ranquear atendentes pelo NPS bruto pune quem tem poucas respostas, cujo NPS é instável. Duas ferramentas resolvem: o <b>gráfico de funil</b> (limites de 95% que se estreitam com o n) e o <b>encolhimento bayesiano empírico</b>, que puxa cada NPS para a média geral na proporção da incerteza:</p>
<p>\\(\\mathrm{{NPS}}^{{aj}}_i = \\bar{{\\mathrm{{NPS}}}} + B_i\\,(\\mathrm{{NPS}}_i-\\bar{{\\mathrm{{NPS}}}}), \\quad B_i = \\dfrac{{\\tau^2}}{{\\tau^2 + \\mathrm{{var}}_i/n_i}}\\)</p>
<img src="img/05_funil_atendentes.png" alt="Gráfico de funil do NPS por atendente — dados fictícios">
<p>Entre os atendentes fictícios com 30+ respostas, o NPS bruto vai de {at_min:.0f} a {at_max:.0f}; ajustado, de {at_min_aj:.0f} a {at_max_aj:.0f}. A dispersão que sobra é real e é a <b>prática boa a multiplicar</b>, não um ranking para punir.</p>

<h2>8. Voz do cliente: temas, monitoria e causa-raiz</h2>
<p>Número diz <i>quanto</i>; comentário diz <i>por quê</i>. Uma classificação multitema por palavras-chave (com anonimização prévia de e-mail, CPF e telefone) já organiza a leitura. Sempre reporte o percentual sem tema: ele é o limite da classificação. Na base fictícia:</p>
<ul>{temas}</ul>
<p>Na monitoria, a auditoria das notas detratoras por pilares de responsabilidade (por exemplo <b>Conhecimento, Operacional, Sistema, Processo e Atitude</b>, como no modelo do Projeto Promotor) separa o que é do atendente do que é do processo. Na prática, a maior parte da detração costuma estar em processo: retorno, prazo e regra.</p>

<h2>9. Do diagnóstico à ação: a árvore de KPIs</h2>
<p>NPS é resultado; quem o move são os indicadores de processo. Ligue cada achado a um KPI que a operação controla:</p>
<ul>
<li><b>Prazo</b> → % de casos acima de 24h, SLA, TME, backlog por idade.</li>
<li><b>Resolutividade</b> → FCR e recontato em 7 dias.</li>
<li><b>Tratativa</b> → nota de monitoria por pilar, CSAT do atendimento, aderência a script.</li>
<li><b>Esforço</b> → CES e número de contatos por caso.</li>
<li><b>Eficiência</b> → TMA e produtividade, sempre lidos junto com qualidade.</li>
</ul>
<p>E leve para o comitê semanal o NPS <b>com margem de erro</b>, o NPS dos grupos críticos e o cenário do modelo. Decisão boa nasce de pergunta boa.</p>

<h2>10. Limites e boas práticas</h2>
<ul>
<li>Mudança de canal da pesquisa (por exemplo, incluir e-mail) muda o perfil de quem responde: trate como quebra de série.</li>
<li>Mês parcial não deve ser comparado com mês fechado.</li>
<li>Mudança de tabulação de motivos cria tendências artificiais.</li>
<li>Correlação entre poucos pontos mensais indica direção, não causa; prefira o nível da resposta.</li>
<li>Comentários e dados de clientes devem ser anonimizados antes da análise.</li>
</ul>

<h2>Como usar o código</h2>
<pre><code>pip install numpy pandas matplotlib
python publicacao.py --saida _site   # gera esta página com a base fictícia

import pandas as pd, nps_toolkit as nt
df = pd.read_csv("sua_base.csv")          # colunas: mes, nota, fatores 0/1...
nt.teste_mes_a_mes(nt.nps_por(df, "mes"))
nt.decomposicao_mix(df, "mes", "faixa_resolucao", "M01", "M02")
nt.modelo_resposta(df, ["lento_24h", "reclamacao", "recontato_7d"])</code></pre>

<h2>Referências</h2>
<ul>
<li>REICHHELD, F. F. The One Number You Need to Grow. <i>Harvard Business Review</i>, dez. 2003.</li>
<li>KEININGHAM, T. L. et al. A Longitudinal Examination of Net Promoter and Firm Revenue Growth. <i>Journal of Marketing</i>, v. 71, n. 3, 2007.</li>
<li>DIXON, M.; FREEMAN, K.; TOMAN, N. Stop Trying to Delight Your Customers. <i>Harvard Business Review</i>, jul.–ago. 2010.</li>
<li>MONTGOMERY, D. C. <i>Introduction to Statistical Quality Control</i>. Wiley.</li>
<li>SPIEGELHALTER, D. J. Funnel plots for comparing institutional performance. <i>Statistics in Medicine</i>, v. 24, n. 8, 2005.</li>
<li>EFRON, B.; MORRIS, C. Data Analysis Using Stein's Estimator and its Generalizations. <i>JASA</i>, v. 70, n. 350, 1975.</li>
<li>WHITE, H. A Heteroskedasticity-Consistent Covariance Matrix Estimator. <i>Econometrica</i>, v. 48, n. 4, 1980.</li>
<li>MACIEL, A. L. Qualidade não é controle. É alavanca estratégica de resultado. Zenodo, 2026. <a href="https://doi.org/10.5281/zenodo.23891606">doi:10.5281/zenodo.23891606</a>.</li>
</ul>
</article>

<section class="box">
<h2 style="margin-top:0">Sobre o autor</h2>
<p><b>André Luiz Maciel</b> é Coordenador de Qualidade, com trajetória que vai do atendimento à coordenação em operações de banco, seguros, varejo, energia e saúde. Une estatística, ciência de dados (SQL, Power BI, Python) e gestão de equipes para transformar indicadores como NPS, CSAT, CES, FCR e recontato em decisão. É co-idealizador do Projeto Promotor e autor da frase <i>“Qualidade não é controle. É alavanca estratégica de resultado.”</i></p>
<p><a href="https://www.linkedin.com/in/andr%C3%A9-luiz-maciel-622a52119/">LinkedIn</a> · <a href="https://medium.com/@andreluizmaciel26">Medium</a> · <a href="https://doi.org/10.5281/zenodo.23891606">Zenodo</a> · <a href="https://projetopromotor-nexus.base44.app/">Projeto Promotor</a> · <a href="{repo}">Código</a></p>
<p><b>Como citar:</b> MACIEL, André Luiz. <i>NPS com rigor estatístico: como separar ruído de mudança real e descobrir o que move o indicador</i>. 2026. Disponível em: {url}.</p>
<p style="font-size:13px;color:var(--muted)">Texto sob CC BY 4.0 · Código sob licença MIT · Dados 100% fictícios.</p>
</section>
</main></body></html>
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default="_site")
    gerar_site(ap.parse_args().saida)
