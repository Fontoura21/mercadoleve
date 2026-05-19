terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Bucket S3 que armazena as imagens de produtos enviadas pelos vendedores.
resource "aws_s3_bucket" "uploads" {
  bucket = "mercadoleve-uploads"
}

resource "aws_s3_bucket_acl" "uploads_acl" {
  bucket = aws_s3_bucket.uploads.id
  acl    = "public-read"
}

# Banco de dados gerenciado (RDS PostgreSQL) da aplicação.
resource "aws_db_instance" "main" {
  identifier          = "mercadoleve-db"
  engine              = "postgres"
  engine_version      = "15.4"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "mercado"
  password            = "mercado123"
  publicly_accessible = true
  storage_encrypted   = false
  skip_final_snapshot = true
}

# Security group da API.
resource "aws_security_group" "api" {
  name        = "mercadoleve-api-sg"
  description = "Permite acesso a API e administracao"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Instância EC2 que roda o container da API.
resource "aws_instance" "api" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = "t3.small"
  vpc_security_group_ids = [aws_security_group.api.id]

  root_block_device {
    encrypted = false
  }

  tags = {
    Name = "mercadoleve-api"
  }
}
