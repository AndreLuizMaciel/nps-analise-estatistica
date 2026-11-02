"""
Gera uma base 100% FICTÍCIA de respostas de NPS de uma central de atendimento
imaginária ("Central Exemplo"). Nenhum número aqui vem de empresa real: as
probabilidades foram escolhidas só para ilustrar os métodos do nps_toolkit.

Autor: André Luiz Maciel · Licença: MIT
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FAIXAS = ["até 1h", "1–4h", "4–24h", "1–3 dias", "> 3 dias"]
CANAIS = ["Chat", "Voz", "E-mail"]
TIPOS = ["Dúvida", "Solicitação", "Reclamação", "Evento sazonal"]

COMENTARIOS = {
    "retorno_prazo": ["Demorou demais para ter retorno.", "Esperei dias e ninguém respondeu.",
                      "Prazo muito longo para algo simples."],
    "sistema_acesso": ["O aplicativo não deixa entrar.", "Não consigo acessar o site.",
                       "O código de acesso nunca chega."],
    "resposta_generica": ["Resposta pronta, não leram o que escrevi.", "Parece robô, resposta genérica.",
                          "Responderam só metade da minha dúvida."],
    "regra_elegibilidade": ["A regra não estava clara.", "Disseram que eu não tinha direito sem explicar o motivo.",
                            "Mudaram a regra no meio do caminho."],
    "outros": ["Não gostei.", "Poderia ser melhor.", "Atendimento ruim."],
}


def gerar(seed: int = 7, meses: int = 12) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    atendentes = [f"AT{i:02d}" for i in range(1, 26)]
    efeito_at = dict(zip(atendentes, rng.normal(0, 0.05, len(atendentes))))
    peso_at = rng.dirichlet(np.ones(len(atendentes)) * 1.5)

    # parâmetros por mês (fictícios)
    lento_mes = np.clip(rng.normal(0.11, 0.05, meses), 0.03, 0.25)
    lento_mes[1] = 0.22                               # um mês com fila acumulada
    sazonal_mes = np.where((np.arange(meses) >= 4) & (np.arange(meses) <= 6), 0.16, 0.02)   # evento sazonal no meio do ano
    email_mes = np.where(np.arange(meses) >= 8, 0.25, 0.0)      # novo canal de pesquisa a partir do M09

    linhas = []
    for m in range(meses):
        n = int(rng.integers(170, 390))
        for _ in range(n):
            canal = "E-mail" if rng.random() < email_mes[m] else ("Voz" if rng.random() < 0.3 else "Chat")
            if rng.random() < sazonal_mes[m]:
                tipo = "Evento sazonal"
            else:
                tipo = rng.choice(["Dúvida", "Solicitação", "Reclamação"], p=[0.5, 0.38, 0.12])
            lento = rng.random() < lento_mes[m]
            faixa = rng.choice(FAIXAS[3:], p=[0.55, 0.45]) if lento else rng.choice(FAIXAS[:3], p=[0.62, 0.22, 0.16])
            recontato = rng.random() < (0.18 if lento else 0.07)
            at = rng.choice(atendentes, p=peso_at)

            p_prom, p_detr = 0.66, 0.12
            ajuste = (0.26 * lento + 0.14 * (tipo == "Reclamação") + 0.30 * (tipo == "Evento sazonal")
                      + 0.09 * (canal == "E-mail") + 0.10 * recontato + efeito_at[at]
                      + rng.normal(0, 0.03))
            p_detr = float(np.clip(p_detr + 0.75 * ajuste, 0.01, 0.95))
            p_prom = float(np.clip(p_prom - 0.9 * ajuste, 0.02, 0.97 - p_detr))
            u = rng.random()
            if u < p_prom:
                nota = int(rng.choice([9, 10], p=[0.35, 0.65]))
            elif u < p_prom + p_detr:
                nota = int(rng.choice(range(0, 7), p=[0.3, 0.1, 0.08, 0.1, 0.1, 0.17, 0.15]))
            else:
                nota = int(rng.choice([7, 8]))

            comentario = ""
            if nota <= 6 and rng.random() < 0.45:
                if lento:
                    tema = "retorno_prazo"
                elif tipo == "Evento sazonal":
                    tema = rng.choice(["regra_elegibilidade", "retorno_prazo"], p=[0.7, 0.3])
                else:
                    tema = rng.choice(list(COMENTARIOS), p=[0.25, 0.2, 0.3, 0.1, 0.15])
                comentario = str(rng.choice(COMENTARIOS[tema]))

            linhas.append({
                "mes": f"M{m + 1:02d}", "canal": canal, "tipo": tipo, "faixa_resolucao": faixa,
                "lento_24h": int(lento), "evento_sazonal": int(tipo == "Evento sazonal"),
                "reclamacao": int(tipo == "Reclamação"), "canal_email": int(canal == "E-mail"),
                "recontato_7d": int(recontato), "atendente": at, "nota": nota, "comentario": comentario,
            })
    df = pd.DataFrame(linhas)
    df["faixa_resolucao"] = pd.Categorical(df["faixa_resolucao"], FAIXAS, ordered=True)
    return df


if __name__ == "__main__":
    base = gerar()
    base.to_csv("base_ficticia.csv", index=False)
    print(base.head(), "\n", len(base), "respostas fictícias geradas.")
