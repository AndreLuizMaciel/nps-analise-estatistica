# NPS com rigor estatístico

**Como separar ruído de mudança real e descobrir o que move o indicador**

Autor: **André Luiz Maciel** · Coordenador de Qualidade · CX · Analytics
📄 Publicação completa: **https://andreluizmaciel.github.io/nps-analise-estatistica/**

> *"Qualidade não é controle. É alavanca estratégica de resultado."* — André Luiz Maciel ([doi:10.5281/zenodo.23891606](https://doi.org/10.5281/zenodo.23891606))

![NPS mensal com margem de erro e carta de controle (dados fictícios)](https://andreluizmaciel.github.io/nps-analise-estatistica/img/01_nps_mensal.png)

---

## Por que este repositório existe

Em centrais de atendimento, o NPS do mês sobe e desce, e cada variação vira uma caça ao culpado. Na maior parte das vezes a variação está **dentro do ruído da amostra**, ou vem de uma **mudança no tipo de caso** e não da qualidade do atendimento.

Este repositório reúne um roteiro estatístico, com código aberto em Python, para responder três perguntas antes de qualquer plano de ação:

1. **A variação é real ou é ruído?** Margem de erro, teste z e carta de controle.
2. **Mudou o tipo de caso ou piorou o mesmo caso?** Decomposição *shift-share* (mix × desempenho).
3. **Quais fatores mais tiram pontos e quanto vale corrigir cada um?** Regressão no nível da resposta e simulação de cenários.

E complementa com análise justa entre atendentes (gráfico de funil e encolhimento bayesiano empírico) e leitura da voz do cliente por temas.

> ⚠️ **Todos os dados são fictícios**, gerados por `dados_sinteticos.py` para uma central imaginária. O foco é o **método**.

## A ideia central em uma linha

Dê a cada resposta o valor **+100** (promotor), **0** (neutro) ou **−100** (detrator). A média desse vetor **é** o NPS. Logo o NPS tem variância e margem de erro:

```
NPS        = 100 · (p+ − p−)
var        = p+ + p− − (p+ − p−)²
margem 95% = 1,96 · √(var / n) · 100
```

Com 300 respostas no mês, a margem costuma passar de ±8 pontos.

## O que tem aqui

| Arquivo | O que faz |
|---|---|
| `nps_toolkit.py` | Funções: `resumo_nps`, `nps_por`, `teste_mes_a_mes`, `limites_controle`, `decomposicao_mix`, `nps_sem_segmento`, `modelo_resposta`, `simular_cenario`, `dispersao_atendentes`, `marcar_temas`, `anonimizar` |
| `dados_sinteticos.py` | Gera uma base 100% fictícia de respostas de NPS |
| `publicacao.py` | Gera a publicação (site com gráficos) a partir da base fictícia |
| `.github/workflows/pages.yml` | Publica o site no GitHub Pages a cada atualização |

## Como usar

```bash
pip install -r requirements.txt
python publicacao.py --saida _site      # gera a publicação com a base fictícia
```

```python
import pandas as pd
import nps_toolkit as nt

df = pd.read_csv("sua_base.csv")   # colunas: mes, nota (0-10) e fatores 0/1

nt.teste_mes_a_mes(nt.nps_por(df, "mes"))                               # ruído ou mudança real?
nt.decomposicao_mix(df, "mes", "faixa_resolucao", "M01", "M02")         # mix × desempenho
modelo = nt.modelo_resposta(df, ["lento_24h", "reclamacao", "recontato_7d"])
nt.simular_cenario(df, modelo, {"lento_24h": 0.05})                     # e se só 5% passassem de 24h?
nt.dispersao_atendentes(df, min_n=30)                                   # funil + encolhimento
```

## Métodos e leitura

| Pergunta | Método | Como ler |
|---|---|---|
| A queda do mês é real? | Teste z da diferença de dois NPS | p < 0,05 → variação acima do ruído |
| O processo saiu do padrão? | Carta de controle com limites por n | Ponto fora dos limites → investigar causa especial |
| Mudou o perfil ou o desempenho? | Shift-share | Mix → demanda/prazo · Desempenho → tratativa |
| Quanto um grupo pesa? | Contrafactual sem o grupo | NPS sem o grupo e % dos detratores que vêm dele |
| Quanto cada fator tira? | MQO com y = +100/0/−100, erros robustos HC1 | Coeficiente = pontos de NPS por resposta |
| Quem é de fato diferente? | Funil + Bayes empírico | Evita punir quem tem poucas respostas |
| Por que o cliente reclama? | Temas por regex + monitoria por pilares | Sempre reporte o % sem tema |

## Da análise à ação: árvore de KPIs

- **Prazo** → % de casos acima de 24h, SLA, TME, backlog por idade
- **Resolutividade** → FCR, recontato em 7 dias
- **Tratativa** → nota de monitoria por pilar (Conhecimento, Operacional, Sistema, Processo, Atitude), CSAT
- **Esforço** → CES, contatos por caso
- **Eficiência** → TMA e produtividade, sempre lidos junto com qualidade

## Referências

- Reichheld, F. F. (2003). *The One Number You Need to Grow*. Harvard Business Review.
- Keiningham, T. L. et al. (2007). *A Longitudinal Examination of Net Promoter and Firm Revenue Growth*. Journal of Marketing, 71(3).
- Dixon, M.; Freeman, K.; Toman, N. (2010). *Stop Trying to Delight Your Customers*. Harvard Business Review.
- Montgomery, D. C. *Introduction to Statistical Quality Control*. Wiley.
- Spiegelhalter, D. J. (2005). *Funnel plots for comparing institutional performance*. Statistics in Medicine, 24(8).
- Efron, B.; Morris, C. (1975). *Data Analysis Using Stein's Estimator and its Generalizations*. JASA, 70(350).
- White, H. (1980). *A Heteroskedasticity-Consistent Covariance Matrix Estimator*. Econometrica, 48(4).

## Sobre o autor

**André Luiz Maciel** é Coordenador de Qualidade, com trajetória que vai do atendimento à coordenação em operações de banco, seguros, varejo, energia e saúde. Une estatística, ciência de dados (SQL, Power BI, Python) e gestão de equipes para transformar NPS, CSAT, CES, FCR e recontato em decisão. Co-idealizador do Projeto Promotor e autor da frase *"Qualidade não é controle. É alavanca estratégica de resultado."*

[LinkedIn](https://www.linkedin.com/in/andr%C3%A9-luiz-maciel-622a52119/) · [Medium](https://medium.com/@andreluizmaciel26) · [Zenodo](https://doi.org/10.5281/zenodo.23891606) · [Projeto Promotor](https://projetopromotor-nexus.base44.app/)

## Como citar

> MACIEL, André Luiz. *NPS com rigor estatístico: como separar ruído de mudança real e descobrir o que move o indicador*. 2026. Disponível em: https://andreluizmaciel.github.io/nps-analise-estatistica/

Código sob licença MIT · Texto sob CC BY 4.0 · Dados 100% fictícios.
