"""Configuração central do MercadoLeve.

As configurações são lidas de variáveis de ambiente, com valores padrão de
desenvolvimento para facilitar o setup local.
"""
import os


class Settings:
    # Banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://mercado:mercado123@db:5432/mercadoleve",
    )

    # Chave usada para assinar os tokens JWT.
    # FIXME: mover para variável de ambiente antes de produção.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-super-secret-key-2023-mercadoleve")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Integração de pagamentos (Stripe)
    STRIPE_API_KEY: str = os.getenv(
        "STRIPE_API_KEY", "sk_live_51Mq8sZKj3xPlaceholderHardcodedKey0099Xy"
    )

    # Bucket S3 onde as imagens de produtos são armazenadas
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "AKIAIOSFODNN7EXAMPLE")
    AWS_SECRET_ACCESS_KEY: str = os.getenv(
        "AWS_SECRET_ACCESS_KEY", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    )
    S3_BUCKET: str = os.getenv("S3_BUCKET", "mercadoleve-uploads")

    # Aplicação
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ALLOWED_ORIGINS = ["*"]


settings = Settings()
