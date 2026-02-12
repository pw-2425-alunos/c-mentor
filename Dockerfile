FROM python:3.11-slim

# Dependências necessárias para MySQL, cryptography e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc pkg-config default-libmysqlclient-dev libssl-dev libffi-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir PyJWT cryptography

COPY . .

ENV PYTHONUNBUFFERED=1 
ENV DJANGO_SETTINGS_MODULE=projeto.settings 
ENV RUN_ENV=CLUSTER

EXPOSE 3000

CMD sh -c "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn projeto.wsgi:application --bind 0.0.0.0:3000 --access-logfile - --error-logfile -"
