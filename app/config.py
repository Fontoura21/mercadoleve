"""Configuração central do MercadoLeve.

Todas as configurações sensíveis são obrigatoriamente lidas de variáveis de
ambiente. Não há segredos embutidos no código-fonte.
"""
import os


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variável de ambiente obrigatória ausente: {name}. "
            "Configure-a antes de iniciar a aplicação."
        )
    return value


class Settings:
    # Banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://mercado@localhost:5432/mercadoleve"
    )

    # Chave usada para assinar os tokens JWT (obrigatória, sem fallback inseguro).
    SECRET_KEY: str = _required("SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Integração de pagamentos (Stripe) — lida do ambiente/segredos.
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")

    # Armazenamento S3 (credenciais via IAM role / variáveis de ambiente).
    S3_BUCKET: str = os.getenv("S3_BUCKET", "mercadoleve-uploads")

    # Aplicação
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Origens permitidas para CORS (lista explícita, nunca "*" com credenciais).
    ALLOWED_ORIGINS = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "https://app.mercadoleve.com").split(",")
        if o.strip()
    ]


settings = Settings()
