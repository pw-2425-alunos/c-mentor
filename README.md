
# C-Mentor Network App

The C-Mentor Network is a web application running at [https://c-mentor.pw.deisi.ulusofona.pt/](https://c-mentor.pw.deisi.ulusofona.pt/) on a university server. 

## How it works

The platform manages mentoring sessions between students, with three types of users:

- **Students**: Can be mentors or mentees.
- **Manager**: Can view all mentors and mentees, see sessions, access a graphical dashboard, report sessions, and add new students.
- **Administrator**: Has full access.

For demo purposes, the database includes 4 students and 2 lectures. You can try the app using the following credentials:

| Name            | Role    | Username | Password  |
|-----------------|---------|----------|-----------|
| Ada Lovelace    | Mentor  | ada      | cmentor   |
| Donald Duck     | Mentee  | donald   | mentor    |
| Manager         | Manager | manager  | mentor    |

> The manager can see all mentors and mentees, view sessions, access the dashboard, report sessions, and add new students.

A short demo video will be included on the landing page soon.

# django-empty

Este repositório serve como um template base para projetos Django, permitindo iniciar rapidamente um novo projeto com uma estrutura pré-configurada.

## Propósito

O `django-empty` foi criado para ser um ponto de partida para projetos Django. Pode clonar este repositório e importar o seu projeto Django existente, aproveitando a configuração inicial já preparada.

## Conteúdo

- **.github/workflows**: Contém os ficheiros de configuração para o pipeline CI/CD, que automatiza o build, push e deploy da imagem Docker.
- **.gitignore**: Define os ficheiros e pastas a serem ignorados pelo Git, como ficheiros temporários e ambientes virtuais.
- **Dockerfile**: Ficheiro de configuração para construir a imagem Docker da aplicação Django. Atenção que `project` deve corresponder ao nome da pasta onde está `settings.py`.
- **docker-compose.yml**: Configuração para orquestrar serviços com Docker Compose, útil para desenvolvimento local.
- **requirements.txt**: Lista as dependências Python necessárias para o projeto.

## Media/Static Files

Em settings.py:
```
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), 
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles') 
```
