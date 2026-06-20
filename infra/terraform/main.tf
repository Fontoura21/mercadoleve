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

# Bucket S3 privado que armazena as imagens de produtos.
resource "aws_s3_bucket" "uploads" {
  bucket = "mercadoleve-uploads"
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket                  = aws_s3_bucket.uploads.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Banco de dados gerenciado (RDS PostgreSQL) da aplicação.
resource "aws_db_instance" "main" {
  identifier                  = "mercadoleve-db"
  engine                      = "postgres"
  engine_version              = "15.4"
  instance_class              = "db.t3.micro"
  allocated_storage           = 20
  username                    = "mercado"
  manage_master_user_password = true
  publicly_accessible         = false
  storage_encrypted           = true
  multi_az                    = true
  deletion_protection         = true
  iam_database_authentication_enabled = true
  backup_retention_period     = 7
  skip_final_snapshot         = false
  final_snapshot_identifier   = "mercadoleve-db-final"
}

# Security group da API — acesso restrito à rede interna.
resource "aws_security_group" "api" {
  name        = "mercadoleve-api-sg"
  description = "Acesso restrito a API MercadoLeve"

  ingress {
    description = "HTTPS interno"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    description = "HTTPS de saida"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Instância EC2 que roda o container da API.
resource "aws_instance" "api" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = "t3.small"
  vpc_security_group_ids = [aws_security_group.api.id]
  monitoring             = true
  ebs_optimized          = true

  metadata_options {
    http_tokens   = "required" # exige IMDSv2
    http_endpoint = "enabled"
  }

  root_block_device {
    encrypted = true
  }

  tags = {
    Name = "mercadoleve-api"
  }
}
