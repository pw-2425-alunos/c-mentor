FROM python:3.11-slim

# Dependências para MySQL, cryptography e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc pkg-config default-libmysqlclient-dev libssl-dev libffi-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir PyJWT cryptography

# Copia código da aplicação
COPY . .

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=projeto.settings
ENV RUN_ENV=CLUSTER

# Porta onde Gunicorn irá ouvir
EXPOSE 3000

# Entry point
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
