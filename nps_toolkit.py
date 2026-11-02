"""
nps_toolkit — leitura estatística do NPS para operações de atendimento.

Autor: André Luiz Maciel
Licença: MIT

Ideia central: o NPS é a média de uma variável que vale +100 (promotor),
0 (neutro) ou -100 (detrator). Tratando o NPS como média, ganhamos todo o
ferramental estatístico clássico: variância, margem de erro, testes de
diferença, decomposição e regressão no nível da resposta.
"""
from __future__ import annotations

import math
import re
import unicodedata

import numpy as np
import pandas as pd

Z95 = 1.959963984540054


# ---------------------------------------------------------------------------
# 1. Fundamentos
# ---------------------------------------------------------------------------
def classificar(nota: int) -> str:
    """0-6 detrator, 7-8 neutro, 9-10 promotor."""
    if nota >= 9:
        return "Promotor"
    if nota >= 7:
        return "Neutro"
    return "Detrator"


def valor_resposta(nota) -> np.ndarray:
    """Converte notas 0-10 em +100 / 0 / -100. A média desse vetor é o NPS."""
    nota = np.asarray(nota)
    return np.where(nota >= 9, 100.0, np.where(nota >= 7, 0.0, -100.0))


def _p_normal(z: float) -> float:
    """p-valor bilateral pela normal padrão."""
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def resumo_nps(notas) -> dict:
    """NPS, proporções, variância de uma resposta e margem de erro de 95%.

    var = p+ + p- - (p+ - p-)^2   (variância de uma resposta que vale +1, 0, -1)
    margem = 1,96 * sqrt(var / n) * 100
    """
    notas = np.asarray(notas)
    n = len(notas)
    if n == 0:
        return {"n": 0, "nps": np.nan, "p_prom": np.nan, "p_detr": np.nan, "var": np.nan, "margem95": np.nan}
    p = np.mean(notas >= 9)
    d = np.mean(notas <= 6)
    var = p + d - (p - d) ** 2
    return {
        "n": n,
        "nps": 100 * (p - d),
        "p_prom": 100 * p,
        "p_detr": 100 * d,
        "var": var,
        "margem95": Z95 * math.sqrt(var / n) * 100,
    }


def nps_por(df: pd.DataFrame, por, col_nota: str = "nota") -> pd.DataFrame:
    """Tabela de NPS com margem de erro para cada grupo."""
    linhas = []
    for chave, g in df.groupby(por, sort=True, observed=True):
        r = resumo_nps(g[col_nota].to_numpy())
        r[por if isinstance(por, str) else "grupo"] = chave
        linhas.append(r)
    out = pd.DataFrame(linhas)
    cols = [c for c in out.columns if c not in ("n", "nps", "p_prom", "p_detr", "var", "margem95")]
    return out[cols + ["n", "p_prom", "p_detr", "nps", "margem95", "var"]]


# ---------------------------------------------------------------------------
# 2. Ruído x mudança real
# ---------------------------------------------------------------------------
def teste_diferenca(a: dict, b: dict) -> dict:
    """Teste z para a diferença entre dois NPS independentes (b - a)."""
    delta = b["nps"] - a["nps"]
    se = math.sqrt(a["var"] / a["n"] + b["var"] / b["n"]) * 100
    z = delta / se if se > 0 else np.nan
    return {"delta": delta, "z": z, "p_valor": _p_normal(z), "significativo_95": abs(z) > Z95}


def teste_mes_a_mes(tabela_mensal: pd.DataFrame) -> pd.DataFrame:
    """Aplica o teste z a cada par de meses consecutivos de uma tabela de nps_por()."""
    t = tabela_mensal.reset_index(drop=True).copy()
    deltas, zs, ps, sig = [np.nan], [np.nan], [np.nan], [False]
    for i in range(1, len(t)):
        r = teste_diferenca(t.iloc[i - 1].to_dict(), t.iloc[i].to_dict())
        deltas.append(r["delta"]); zs.append(r["z"]); ps.append(r["p_valor"]); sig.append(r["significativo_95"])
    t["delta"], t["z"], t["p_valor"], t["significativo_95"] = deltas, zs, ps, sig
    return t


def limites_controle(tabela_mensal: pd.DataFrame, sigmas: float = 3.0) -> pd.DataFrame:
    """Carta de controle do NPS: linha central = NPS do período todo,
    limites = centro ± k * sqrt(var_global / n_mes) * 100 (limites variam com o n do mês)."""
    t = tabela_mensal.copy()
    n_tot = t["n"].sum()
    p = (t["p_prom"] / 100 * t["n"]).sum() / n_tot
    d = (t["p_detr"] / 100 * t["n"]).sum() / n_tot
    centro = 100 * (p - d)
    var = p + d - (p - d) ** 2
    t["centro"] = centro
    t["lsc"] = centro + sigmas * np.sqrt(var / t["n"]) * 100
    t["lic"] = centro - sigmas * np.sqrt(var / t["n"]) * 100
    t["fora_de_controle"] = (t["nps"] > t["lsc"]) | (t["nps"] < t["lic"])
    return t


# ---------------------------------------------------------------------------
# 3. Mix x desempenho (shift-share)
# ---------------------------------------------------------------------------
def decomposicao_mix(df: pd.DataFrame, periodo: str, segmento: str, p0, p1, col_nota: str = "nota") -> pd.DataFrame:
    """Decompõe a variação do NPS entre p0 e p1 em efeito mix e efeito desempenho.

    Mix        = Σ (w1 - w0) * NPS0_g        -> mudou a composição dos casos
    Desempenho = Σ w1 * (NPS1_g - NPS0_g)    -> o mesmo tipo de caso foi avaliado diferente
    Mix + Desempenho = NPS1 - NPS0 (identidade exata)
    """
    def tab(p):
        g = df[df[periodo] == p]
        t = g.groupby(segmento, observed=True)[col_nota].agg(
            n="size", nps=lambda s: 100 * (np.mean(s >= 9) - np.mean(s <= 6)))
        t["w"] = t["n"] / t["n"].sum()
        return t

    a, b = tab(p0), tab(p1)
    seg = a.index.union(b.index)
    a = a.reindex(seg).fillna({"n": 0, "w": 0})
    b = b.reindex(seg).fillna({"n": 0, "w": 0})
    # segmento ausente em um dos períodos: usa o NPS do outro período (efeito só de mix)
    a["nps"] = a["nps"].fillna(b["nps"])
    b["nps"] = b["nps"].fillna(a["nps"])
    out = pd.DataFrame({
        "w0": a["w"], "w1": b["w"], "nps0": a["nps"], "nps1": b["nps"],
        "mix": (b["w"] - a["w"]) * a["nps"],
        "desempenho": b["w"] * (b["nps"] - a["nps"]),
    })
    out.loc["TOTAL"] = [1, 1, (a["w"] * a["nps"]).sum(), (b["w"] * b["nps"]).sum(),
                        out["mix"].sum(), out["desempenho"].sum()]
    return out


def nps_sem_segmento(df: pd.DataFrame, mascara, col_nota: str = "nota") -> dict:
    """Contrafactual simples: NPS com e sem um grupo de respostas e a parcela
    dos detratores que vem desse grupo."""
    total = resumo_nps(df[col_nota])
    sem = resumo_nps(df.loc[~mascara, col_nota])
    so = resumo_nps(df.loc[mascara, col_nota])
    detr = df[col_nota] <= 6
    return {
        "nps_total": total["nps"], "nps_sem_grupo": sem["nps"], "nps_do_grupo": so["nps"],
        "peso_grupo_%": 100 * mascara.mean(),
        "parcela_detratores_%": 100 * (detr & mascara).sum() / max(detr.sum(), 1),
    }


# ---------------------------------------------------------------------------
# 4. Modelo no nível da resposta
# ---------------------------------------------------------------------------
def modelo_resposta(df: pd.DataFrame, fatores: list[str], col_nota: str = "nota") -> pd.DataFrame:
    """Regressão linear (MQO) com y = +100/0/-100 e fatores binários (0/1).

    Como a média de y é o NPS, cada coeficiente se lê em "pontos de NPS":
    é quanto aquele fator tira (ou soma) de cada resposta, mantidos os demais.
    O intercepto é o NPS esperado do caso-base (todos os fatores = 0).
    Erros-padrão robustos (HC1), porque y tem só três valores.
    """
    y = valor_resposta(df[col_nota].to_numpy())
    X = np.column_stack([np.ones(len(df))] + [df[f].astype(float).to_numpy() for f in fatores])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = X.T @ (X * (resid ** 2)[:, None])
    cov = XtX_inv @ meat @ XtX_inv * n / (n - k)
    se = np.sqrt(np.diag(cov))
    t = beta / se
    return pd.DataFrame({"coef": beta, "erro_padrao": se, "t": t,
                         "p_valor": [_p_normal(v) for v in t]},
                        index=["intercepto (caso-base)"] + fatores)


def simular_cenario(df: pd.DataFrame, modelo: pd.DataFrame, mudancas: dict, col_nota: str = "nota") -> float:
    """NPS esperado se a participação de cada fator mudar.
    mudancas = {"fator": nova_participacao (0-1)}"""
    nps_atual = resumo_nps(df[col_nota])["nps"]
    ajuste = 0.0
    for f, nova in mudancas.items():
        ajuste += (nova - df[f].mean()) * modelo.loc[f, "coef"]
    return nps_atual + ajuste


# ---------------------------------------------------------------------------
# 5. Dispersão entre atendentes (sem ranking injusto)
# ---------------------------------------------------------------------------
def dispersao_atendentes(df: pd.DataFrame, col_atendente: str = "atendente", min_n: int = 30,
                         col_nota: str = "nota") -> pd.DataFrame:
    """NPS por atendente com encolhimento bayesiano empírico.

    Atendente com poucas respostas tem NPS muito instável. O encolhimento puxa
    cada NPS para a média geral na proporção da incerteza:
        NPS_aj = media + B * (NPS_i - media),  B = tau² / (tau² + var_i/n_i)
    """
    t = nps_por(df, col_atendente, col_nota)
    geral = resumo_nps(df[col_nota])
    t["se"] = np.sqrt(t["var"] / t["n"]) * 100
    elegiveis = t[t["n"] >= min_n]
    tau2 = max(elegiveis["nps"].var(ddof=1) - (elegiveis["se"] ** 2).mean(), 1e-9)
    B = tau2 / (tau2 + t["se"] ** 2)
    t["nps_ajustado"] = geral["nps"] + B * (t["nps"] - geral["nps"])
    t["elegivel"] = t["n"] >= min_n
    # limites do funil (95%) para cada tamanho de amostra
    t["funil_inf"] = geral["nps"] - Z95 * np.sqrt(geral["var"] / t["n"]) * 100
    t["funil_sup"] = geral["nps"] + Z95 * np.sqrt(geral["var"] / t["n"]) * 100
    return t.sort_values("nps_ajustado", ascending=False)


# ---------------------------------------------------------------------------
# 6. Voz do cliente: temas por palavra-chave
# ---------------------------------------------------------------------------
def _normalizar(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", str(txt).lower())
    return "".join(c for c in txt if not unicodedata.combining(c))


def marcar_temas(textos: pd.Series, regras: dict[str, str]) -> pd.DataFrame:
    """Classificação multitema por expressões regulares (um comentário pode ter
    vários temas). Retorna uma coluna 0/1 por tema e a coluna 'sem_tema'.
    Sempre reporte o % sem tema: é o limite de qualidade da classificação."""
    norm = textos.fillna("").map(_normalizar)
    out = pd.DataFrame({tema: norm.str.contains(rx, regex=True).astype(int) for tema, rx in regras.items()},
                       index=textos.index)
    out["sem_tema"] = (out.sum(axis=1) == 0).astype(int)
    return out


def anonimizar(txt: str) -> str:
    """Mascara e-mail, CPF, telefone e números longos antes de qualquer análise."""
    txt = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", str(txt))
    txt = re.sub(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", "[cpf]", txt)
    txt = re.sub(r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}", "[telefone]", txt)
    txt = re.sub(r"\d{12,19}", "[numero]", txt)
    return txt
