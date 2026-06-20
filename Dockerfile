FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instala dependências primeiro (melhor uso de cache) com usuário root,
# antes de rebaixar privilégios.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas o necessário (sem segredos, sem contexto desnecessário).
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY static/ ./static/

# Cria e usa um usuário não-privilegiado.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
