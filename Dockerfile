FROM python:latest

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia todo o contexto (inclui código, configs e arquivos auxiliares)
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
