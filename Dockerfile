FROM python:3.11-slim

# Dependências para MySQL, cryptography e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc pkg-config default-libmysqlclient-dev libssl-dev libffi-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir PyJWT cryptography

# Copiar todo o código
COPY . .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=projeto.settings
ENV RUN_ENV=CLUSTER

EXPOSE 3000

# Healthcheck simples
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=5 \
  CMD curl -f http://localhost:3000/health/ || exit 1

# Script CMD robusto
CMD sh -c "\
    echo 'Migrating database...' && \
    python manage.py migrate --noinput && \
    echo 'Collecting static files...' && \
    python manage.py collectstatic --noinput || true && \
    echo 'Starting Gunicorn...' && \
    gunicorn projeto.wsgi:application --bind 0.0.0.0:3000 --workers 3 --threads 2 \
    --access-logfile - --error-logfile - \
"
