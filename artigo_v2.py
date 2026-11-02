"""Gera o PDF da versão 2.0 do artigo de André Luiz Maciel.
Uso: python artigo_v2.py saida.pdf · Texto sob CC BY 4.0. Conteúdo conceitual, sem dados de empresa.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os, sys
import matplotlib

_FD = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
for nome, arq in [('DV', 'DejaVuSans.ttf'), ('DV-B', 'DejaVuSans-Bold.ttf'), ('DV-I', 'DejaVuSans-Oblique.ttf'),
                  ('DV-BI', 'DejaVuSans-BoldOblique.ttf'), ('DVM', 'DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(nome, os.path.join(_FD, arq)))
addMapping('DV', 0, 0, 'DV'); addMapping('DV', 1, 0, 'DV-B'); addMapping('DV', 0, 1, 'DV-I'); addMapping('DV', 1, 1, 'DV-BI')
SAIDA = sys.argv[1] if len(sys.argv) > 1 else 'artigo-v2.pdf'

ACC = colors.HexColor('#0b6e4f')
base = ParagraphStyle('b', fontName='DV', fontSize=10.3, leading=14.6, spaceAfter=6.5, alignment=4)
S = {
    'k': ParagraphStyle('k', parent=base, fontName='DV-B', fontSize=8.5, textColor=ACC, alignment=0),
    'h1': ParagraphStyle('h1', parent=base, fontName='DV-B', fontSize=19, leading=23, alignment=0, spaceAfter=4),
    'sub': ParagraphStyle('sub', parent=base, fontName='DV', fontSize=12, leading=16, alignment=0, textColor=colors.HexColor('#333333')),
    'by': ParagraphStyle('by', parent=base, fontSize=9.3, textColor=colors.HexColor('#5b6470'), alignment=0),
    'h2': ParagraphStyle('h2', parent=base, fontName='DV-B', fontSize=12.5, leading=16, spaceBefore=9, spaceAfter=4, alignment=0, keepWithNext=1),
    'q': ParagraphStyle('q', parent=base, fontName='DV-B', fontSize=12.5, leading=17, leftIndent=10, backColor=colors.HexColor('#eef5f2'), borderPadding=6, alignment=0),
    'f': ParagraphStyle('f', parent=base, fontName='DVM', fontSize=9.3, leading=13, leftIndent=12, alignment=0, backColor=colors.HexColor('#f4f6f8'), borderPadding=4),
    's': ParagraphStyle('s', parent=base, fontSize=8.8, leading=12, alignment=0),
    'li': ParagraphStyle('li', parent=base, leftIndent=12, bulletIndent=2, spaceAfter=3),
}
F = []
P = lambda t, s=None: F.append(Paragraph(t, S[s] if s else base))
H = lambda t: P(t, 'h2')
def L(items):
    for it in items:
        F.append(Paragraph(it, S['li'], bulletText='•'))
def T(rows, widths):
    data = [[Paragraph(c, S['s']) for c in r] for r in rows]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cfd6dc')),
                           ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eef5f2')),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    F.append(t); F.append(Spacer(1, 6))

MED = 'https://medium.com/@andreluizmaciel26/qualidade-n%C3%A3o-%C3%A9-controle-%C3%A9-alavanca-estrat%C3%A9gica-de-resultado-09eb56f01c5e'
GH = 'https://github.com/AndreLuizMaciel/nps-analise-estatistica'
SITE = 'https://andreluizmaciel.github.io/nps-analise-estatistica/'

P('ARTIGO · QUALIDADE EM CALL CENTER · VERSÃO 2.0 (AMPLIADA)', 'k')
P('Qualidade não é controle. É alavanca estratégica de resultado', 'h1')
P('Da monitoria à leitura estatística do NPS: KPIs, causa-raiz e decisão em operações de call center', 'sub')
P('<b>André Luiz Maciel</b> (Andre Luiz Maciel de Lima Silva) · Versão 1.0 publicada em 6 abr. 2026 (Medium) · Versão 2.0 ampliada em nov. 2026', 'by')
P('<i>Quality is not control. It is a strategic lever for results. · Calidad no es control. Es una palanca estratégica de resultados.</i>')

H('Resumo')
P('Este artigo analisa o reposicionamento estratégico da área de Qualidade em operações de call center, compreendendo-a não mais como um mecanismo estritamente normativo, mas como um elemento central de geração de valor organizacional. Discute-se a integração entre Qualidade, Customer Experience (CX) e Customer Success (CS), bem como o uso intensivo de dados, metodologias de melhoria contínua e Inteligência Artificial (IA) como suportes à tomada de decisão. Nesta versão ampliada, o artigo acrescenta (i) uma árvore de indicadores que liga os KPIs de processo do call center ao NPS e ao resultado financeiro, (ii) um roteiro estatístico para ler o NPS com margem de erro, testes de significância, decomposição mix × desempenho e regressão no nível da resposta, e (iii) um modelo de monitoria orientada à causa-raiz por pilares de responsabilidade. Os métodos são apresentados de forma conceitual, com exemplos numéricos fictícios e código aberto.')
P('<b>Palavras-chave:</b> Qualidade; NPS; Customer Experience; Customer Success; Call Center; Estatística aplicada; KPIs; Inteligência Artificial; Melhoria Contínua.')

H('1. Introdução')
P('A intensificação da competitividade no setor de serviços tem ampliado a relevância da experiência do cliente como fator crítico de diferenciação organizacional. Em operações de call center, caracterizadas por alto volume de interações e elevada exposição à percepção do cliente, a qualidade assume papel estrutural na sustentação da estratégia corporativa.')
P('Tradicionalmente associada a práticas de controle, auditoria e conformidade, a área de Qualidade vem sendo progressivamente ressignificada. Estudos contemporâneos indicam que organizações orientadas à experiência do cliente superam financeiramente seus concorrentes ao utilizar dados operacionais como insumo estratégico (McKINSEY &amp; COMPANY, 2021). Nesse contexto, a qualidade passa a ser compreendida como catalisadora de decisões gerenciais e resultados de longo prazo.')
P('Há, porém, uma condição para que isso aconteça: a Qualidade precisa ler os números com método. Na prática, muitas operações discutem a variação mensal do NPS sem considerar o erro de amostra, confundem mudança no perfil dos casos com piora no atendimento e respondem a cada oscilação com novas cobranças. Esta versão do artigo propõe um caminho para evitar esses erros.')

H('2. Evolução da Qualidade em Operações de Call Center')
P('Historicamente, os modelos de gestão da qualidade em call centers eram reativos, concentrados na identificação posterior de falhas. Essa abordagem, baseada em inspeção e punição, apresentava limitações quanto à prevenção de erros e ao desenvolvimento das equipes.')
P('Com o avanço da gestão por processos e da análise de dados, a qualidade evolui para uma lógica preditiva e estratégica. Conforme apontado pela Harvard Business Review, organizações que utilizam dados operacionais para antecipar problemas apresentam maior eficiência e melhor experiência percebida pelo cliente (HARVARD BUSINESS REVIEW, 2020). A evolução pode ser resumida em quatro estágios:')
T([['Estágio', 'Pergunta central', 'Ferramentas típicas'],
   ['Reativo (inspeção)', 'O atendente seguiu o script?', 'Checklist de monitoria, nota de conformidade'],
   ['Preventivo', 'Onde os erros se repetem?', 'Calibração, feedback estruturado, treinamento dirigido'],
   ['Preditivo', 'O que vai piorar o indicador?', 'Correlação de KPIs, alertas de prazo, speech analytics'],
   ['Estratégico', 'O que move o resultado e quanto vale corrigir?', 'Modelos estatísticos, cenários, governança com a liderança']],
  [38, 58, 70])

H('3. Qualidade como Alavanca Estratégica de Resultado')
F.append(Paragraph('“Qualidade não é controle. É alavanca estratégica de resultado.”<br/><font size="10" color="#5b6470">— André Luiz Maciel</font>', S['q'])); F.append(Spacer(1, 6))
P('Essa afirmação sintetiza a mudança paradigmática da função qualidade. Para além da verificação de aderência a scripts e normas, a área passa a atuar como elo entre operação e estratégia organizacional, transformando dados qualitativos e quantitativos em conhecimento aplicado.')
P('Segundo a Forrester Research (2022), empresas com alto nível de maturidade em práticas de qualidade apresentam ganhos significativos em eficiência operacional e satisfação do cliente, evidenciando a correlação entre qualidade estratégica e desempenho organizacional.')

H('4. A árvore de KPIs: do processo ao resultado')
P('O NPS é um indicador de resultado: ele registra a percepção, mas não diz o que fazer. Quem o move são os indicadores de processo, que a operação controla. A Qualidade ganha força quando organiza esses indicadores em uma árvore causal:')
T([['Camada', 'Indicadores', 'O que revela'],
   ['Processo e prazo', 'SLA, TME, % de casos acima de 24h, backlog por idade', 'Se o cliente esperou além do que considera razoável'],
   ['Resolutividade', 'FCR (resolução no primeiro contato), recontato em 7 dias', 'Se o problema foi de fato resolvido'],
   ['Tratativa', 'Nota de monitoria por pilar, aderência, CSAT do atendimento', 'Como o caso foi conduzido pelo atendente'],
   ['Esforço', 'CES, número de contatos por caso, troca de canal', 'Quanto custou ao cliente resolver'],
   ['Eficiência', 'TMA, produtividade, ocupação', 'Custo da operação (sempre lido junto com qualidade)'],
   ['Percepção e resultado', 'NPS, CSAT, reclamações públicas, retenção, churn', 'O efeito acumulado de todas as camadas acima']],
  [32, 66, 68])
P('Uma regra prática decorre da árvore: toda meta de eficiência (por exemplo, reduzir TMA) deve vir acompanhada de um indicador de resolutividade (FCR ou recontato). Caso contrário, a operação ganha minutos e perde clientes.')

H('5. Integração entre Qualidade e Customer Experience (CX)')
P('A experiência do cliente constitui-se como variável dependente da consistência operacional. Monitorias, análises de jornada e feedbacks estruturados permitem identificar pontos críticos de atrito e oportunidades de melhoria ao longo do ciclo de atendimento.')
P('Pesquisas indicam que melhorias sistemáticas em CX estão associadas a aumentos de retenção superiores a 5%, com impactos diretos na rentabilidade (McKINSEY &amp; COMPANY, 2021). Assim, a qualidade funciona como base empírica para a gestão da experiência, fornecendo dados confiáveis para intervenções assertivas. Vale lembrar ainda que reduzir o esforço do cliente tende a ser mais eficaz para a lealdade do que tentar “encantá-lo” (DIXON; FREEMAN; TOMAN, 2010).')

H('6. Relação entre Qualidade e Customer Success (CS)')
P('O Customer Success está relacionado à capacidade da organização de garantir entrega contínua de valor ao cliente. A qualidade contribui para esse objetivo ao identificar falhas recorrentes, inconsistências processuais e riscos de insatisfação que podem comprometer a permanência do cliente.')
P('De acordo com a Harvard Business Review (2019), estratégias de CS fundamentadas em dados operacionais reduzem churn e ampliam o lifetime value, reforçando a importância da integração entre qualidade e gestão de relacionamento.')

H('7. Leitura estatística do NPS: ruído, mudança real e fatores')
P('O NPS (REICHHELD, 2003) é normalmente apresentado como “% de promotores menos % de detratores”. Uma forma mais útil de vê-lo é como uma <b>média</b>: atribuindo +100 a cada promotor (notas 9–10), 0 a cada neutro (7–8) e −100 a cada detrator (0–6), a média desses valores é exatamente o NPS. Como toda média, ele tem variância e erro de amostra.')
F.append(Paragraph('NPS = 100 × (p+ − p−)<br/>var = p+ + p− − (p+ − p−)²<br/>margem de erro (95%) = 1,96 × √(var / n) × 100', S['f'])); F.append(Spacer(1, 6))
P('<b>Exemplo numérico (fictício).</b> Um mês com 300 respostas, 60% de promotores e 15% de detratores tem NPS = 45. A variância é 0,60 + 0,15 − 0,45² = 0,5475 e a margem de erro é 1,96 × √(0,5475/300) × 100 ≈ <b>±8,4 pontos</b>. Uma queda de 45 para 40 no mês seguinte, portanto, pode ser apenas ruído. A partir dessa base, propõe-se um roteiro em seis passos:')
L(['<b>Teste mês contra mês.</b> z = (NPS₂ − NPS₁) / [100 × √(var₁/n₁ + var₂/n₂)]. Só se explica uma variação depois de verificar que ela supera o erro de amostra; comparar blocos de meses aumenta o n e revela mudanças de patamar.',
   '<b>Carta de controle.</b> Linha central igual ao NPS do período e limites de ±3σ ajustados ao n de cada mês (MONTGOMERY). Ponto fora dos limites indica causa especial a investigar.',
   '<b>Decomposição mix × desempenho (shift-share).</b> ΔNPS = Σ(w₁ − w₀)·NPS₀ + Σw₁·(NPS₁ − NPS₀). O primeiro termo mede a mudança no perfil dos casos (por exemplo, mais casos lentos); o segundo, a mudança na avaliação do mesmo tipo de caso. Mix pede gestão de demanda e prazo; desempenho pede ação de tratativa.',
   '<b>Contrafactual por grupo.</b> Calcular o NPS com e sem um grupo de casos e a parcela dos detratores que vem dele. Esse passo mostra quando a causa está fora da central, em regra, comunicação ou prazo do produto.',
   '<b>Regressão no nível da resposta.</b> Com y ∈ {+100, 0, −100} e fatores binários (resolvido após 24h, recontato, reclamação, canal), cada coeficiente se lê em pontos de NPS por resposta; o intercepto é o NPS esperado do caso-base. Com erros-padrão robustos (WHITE, 1980), o modelo permite simular cenários: quanto o NPS sobe se metade dos casos lentos for resolvida no prazo.',
   '<b>Comparação justa entre atendentes.</b> O gráfico de funil (SPIEGELHALTER, 2005) e o encolhimento bayesiano empírico (EFRON; MORRIS, 1975) evitam ranquear como “pior” quem só tem poucas respostas. A dispersão que sobra é prática boa a multiplicar.'])
P('O roteiro completo, com código aberto em Python e base de dados 100% fictícia, está disponível em ' + f'<link href="{GH}" color="#0b6e4f">{GH}</link> e na publicação técnica <link href="{SITE}" color="#0b6e4f">{SITE}</link>.')

H('8. Monitoria orientada à causa-raiz')
P('Número diz <i>quanto</i>; a monitoria diz <i>por quê</i>. Em vez de uma nota única de conformidade, propõe-se auditar as notas detratoras por pilares de responsabilidade. No modelo do Projeto Promotor, do qual o autor é co-idealizador, os pilares são <b>Conhecimento, Operacional, Sistema, Processo e Atitude</b>. Essa classificação separa o que é responsabilidade do atendente (conhecimento, atitude) do que é do processo, do sistema ou da regra de negócio. Na experiência prática, uma parcela relevante da detração costuma estar em processo: retorno, prazo e elegibilidade, e não na postura do atendente.')
P('A voz do cliente complementa a monitoria. Uma classificação multitema por palavras-chave, aplicada aos comentários da pesquisa após anonimização (e-mail, documento, telefone), já organiza os principais motivos. O percentual de comentários sem tema deve ser sempre reportado, porque ele é o limite de qualidade da classificação. Reclamações em canais públicos funcionam como espelho externo dos mesmos temas.')

H('9. Inteligência Artificial aplicada à Qualidade')
P('O avanço da Inteligência Artificial tem ampliado significativamente o escopo de atuação da qualidade em call centers. Ferramentas de speech analytics, machine learning e análise preditiva permitem avaliar grandes volumes de interações, identificar padrões comportamentais e antecipar riscos operacionais.')
P('Estudos da McKinsey apontam que o uso de IA em operações de atendimento pode elevar a produtividade em até 30% e melhorar indicadores de satisfação do cliente de forma consistente (McKINSEY &amp; COMPANY, 2022). Assim, a IA deixa de ser um recurso tecnológico isolado e torna-se parte integrante da estratégia de qualidade. A estatística da seção 7 continua necessária: mesmo com 100% das interações analisadas por IA, o NPS segue sendo uma amostra de quem respondeu à pesquisa.')

H('10. Melhoria Contínua e Metodologias Estruturadas')
P('A aplicação de metodologias como PDCA, DMAIC e análise de causa raiz sustenta uma abordagem científica para resolução de problemas. Essas práticas reforçam a tomada de decisão baseada em evidências, reduzindo subjetividades e aumentando a previsibilidade dos resultados. O roteiro estatístico se encaixa naturalmente no DMAIC:')
T([['Fase DMAIC', 'Aplicação ao NPS'],
   ['Definir', 'Qual variação importa: mês, bloco de meses, grupo de casos'],
   ['Medir', 'NPS com margem de erro, carta de controle, base ligada ao caso (tempo, canal, tipo)'],
   ['Analisar', 'Shift-share, contrafactual, regressão no nível da resposta, monitoria por pilares'],
   ['Melhorar', 'Ações por camada da árvore de KPIs, priorizadas pelo cenário do modelo'],
   ['Controlar', 'Ritual semanal com NPS + margem, % de casos lentos, recontato e NPS dos grupos críticos']],
  [35, 131])
P('A qualidade, nesse contexto, atua como facilitadora do ciclo de aprendizagem organizacional, promovendo evolução contínua dos processos e das equipes (FORRESTER RESEARCH, 2021).')

H('11. Impacto da Qualidade e CX nos Resultados Organizacionais')
P('<b>Tabela — Impactos da maturidade em Qualidade e CX nos resultados organizacionais</b>')
T([['Dimensão analisada', 'Baixa maturidade em Qualidade', 'Alta maturidade em Qualidade'],
   ['Satisfação do cliente (CSAT)', 'Instável', 'Consistente e crescente'],
   ['Retrabalho', 'Elevado', 'Reduzido'],
   ['Produtividade', 'Baixa previsibilidade', 'Alta previsibilidade'],
   ['Retenção de clientes', 'Vulnerável', 'Sustentável'],
   ['Resultado financeiro', 'Reativo', 'Estratégico'],
   ['Leitura do NPS', 'Variação mensal discutida sem margem de erro', 'Margem, significância e decomposição antes de agir'],
   ['Monitoria', 'Nota de conformidade e punição', 'Causa-raiz por pilar e desenvolvimento'],
   ['Relação com a liderança', 'Relatório de falhas', 'Cenários e prioridades de investimento']],
  [45, 60, 61])
P('Fonte: elaboração própria, com base em McKinsey (2021) e Forrester (2022); linhas finais acrescentadas nesta versão.', 's')

H('12. Papel da Liderança na Gestão da Qualidade')
P('A liderança exerce papel determinante na consolidação da qualidade como ferramenta estratégica. Gestores são responsáveis por interpretar dados, transformar informações em ações gerenciais e fomentar uma cultura orientada à melhoria contínua.')
P('Organizações com líderes orientados a dados apresentam maior capacidade de adaptação e inovação em ambientes complexos (HARVARD BUSINESS REVIEW, 2020). Na prática, isso se traduz em um ritual simples: um comitê semanal que olha o NPS com margem de erro, os indicadores de processo da árvore de KPIs e o cenário de ganho de cada ação, e que separa o que a central resolve do que precisa ser levado ao cliente contratante.')

H('13. Considerações Finais')
P('A qualidade em operações de call center deve ser compreendida como elemento central da estratégia organizacional. Sua integração com CX, CS e Inteligência Artificial possibilita uma gestão orientada por evidências, centrada no cliente e voltada à geração de resultados sustentáveis.')
P('A evolução da qualidade representa, portanto, não apenas uma mudança operacional, mas um diferencial competitivo relevante em mercados cada vez mais orientados à experiência. Quando a Qualidade lê o NPS com rigor estatístico, liga cada achado a um KPI de processo e leva cenários à liderança, ela deixa de ser controle e passa a ser, de fato, alavanca estratégica de resultado.')

H('Referências')
for r in [
    'DIXON, M.; FREEMAN, K.; TOMAN, N. Stop Trying to Delight Your Customers. <i>Harvard Business Review</i>, jul.–ago. 2010.',
    'EFRON, B.; MORRIS, C. Data Analysis Using Stein’s Estimator and its Generalizations. <i>Journal of the American Statistical Association</i>, v. 70, n. 350, 1975.',
    'FORRESTER RESEARCH. <i>The Forrester CX Index™</i>. Cambridge, 2021.',
    'FORRESTER RESEARCH. <i>Customer Experience Drives Business Growth</i>. Cambridge, 2022.',
    'HARVARD BUSINESS REVIEW. <i>The New Science of Customer Satisfaction</i>. Boston, 2019.',
    'HARVARD BUSINESS REVIEW. <i>Data-Driven Decision Making</i>. Boston, 2020.',
    'KEININGHAM, T. L. et al. A Longitudinal Examination of Net Promoter and Firm Revenue Growth. <i>Journal of Marketing</i>, v. 71, n. 3, 2007.',
    'McKINSEY &amp; COMPANY. <i>The Business Value of Customer Experience</i>. New York, 2021.',
    'McKINSEY &amp; COMPANY. <i>Artificial Intelligence in Customer Operations</i>. New York, 2022.',
    'MONTGOMERY, D. C. <i>Introduction to Statistical Quality Control</i>. Hoboken: Wiley.',
    'REICHHELD, F. F. The One Number You Need to Grow. <i>Harvard Business Review</i>, dez. 2003.',
    'SPIEGELHALTER, D. J. Funnel plots for comparing institutional performance. <i>Statistics in Medicine</i>, v. 24, n. 8, 2005.',
    'WHITE, H. A Heteroskedasticity-Consistent Covariance Matrix Estimator and a Direct Test for Heteroskedasticity. <i>Econometrica</i>, v. 48, n. 4, 1980.',
]:
    P(r, 's')

F.append(Spacer(1, 8))
F.append(KeepTogether([
    Paragraph('Sobre o autor', S['h2']),
    Paragraph('<b>André Luiz Maciel</b> é Coordenador de Qualidade, com trajetória que vai do atendimento à coordenação em operações de banco, seguros, varejo, energia e saúde. Une estatística, ciência de dados (SQL, Power BI, Python) e gestão de equipes para transformar indicadores como NPS, CSAT, CES, FCR e recontato em decisão. É co-idealizador do Projeto Promotor e autor da frase “Qualidade não é controle. É alavanca estratégica de resultado.”', base),
    Paragraph(f'LinkedIn: https://www.linkedin.com/in/andr%C3%A9-luiz-maciel-622a52119/ · Código: {GH} · Versão 1.0: {MED}', S['s']),
    Paragraph('<b>Como citar:</b> MACIEL, André Luiz. Qualidade não é controle. É alavanca estratégica de resultado: da monitoria à leitura estatística do NPS. Versão 2.0. Zenodo, 2026.', S['s']),
]))


def rodape(c, d):
    c.saveState(); c.setFont('DV', 7); c.setFillColor(colors.HexColor('#777777'))
    c.drawCentredString(A4[0] / 2, 12 * mm, f'André Luiz Maciel · Qualidade não é controle. É alavanca estratégica de resultado · v2.0 · {d.page}')
    c.restoreState()


SimpleDocTemplate(SAIDA, pagesize=A4,
                  leftMargin=21 * mm, rightMargin=21 * mm, topMargin=18 * mm, bottomMargin=20 * mm,
                  title='Qualidade não é controle. É alavanca estratégica de resultado (v2.0)', author='André Luiz Maciel',
                  subject='Da monitoria à leitura estatística do NPS em operações de call center',
                  keywords='Qualidade não é controle; alavanca estratégica de resultado; André Luiz Maciel; NPS; call center; KPIs; estatística').build(F, onFirstPage=rodape, onLaterPages=rodape)
print('ok')
