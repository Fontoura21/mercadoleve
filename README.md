# MercadoLeve

API de marketplace/e-commerce construída com **FastAPI + PostgreSQL**.

Permite cadastro de usuários e vendedores, publicação e busca de produtos,
carrinho de compras, checkout com integração de pagamento, avaliações de
produtos e um painel administrativo (relatórios, backup e importação de
catálogo).

## Stack
- Python 3.11 / FastAPI
- PostgreSQL 15 (SQLAlchemy ORM)
- Docker / docker-compose
- Infra como código: Terraform (AWS) e manifestos Kubernetes

## Executando localmente
```bash
docker compose up --build
# API em http://localhost:8000  (docs em /docs)
docker compose exec api python -m scripts.seed
```

## Estrutura
- `app/` — código da aplicação (routers, modelos, auth)
- `infra/terraform` — provisionamento AWS (S3, RDS, EC2, SG)
- `infra/k8s` — manifestos de deployment
- `.github/workflows` — pipeline DevSecOps (CI/CD de segurança)
