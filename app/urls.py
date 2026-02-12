"""projeto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path, include

app_name = 'horarios'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('horarios/', views.horarios_view, name='horarios'),
    path('disciplinas/', views.disciplinas_view, name='disciplinas'),
    path('disciplina/<str:disciplina_id>', views.disciplina_view, name='disciplina'),


    path('utentes/', views.utentes_view, name='utentes'),
    path('utente/<int:utente_id>', views.utente_view, name='utente'),
    path('edita_utente/<int:utente_id>', views.edita_utente_view, name='edita_utente'),
    path('ocorrencia/<int:utente_id>/<int:ocorrencia_id>', views.ocorrencia_view, name='ocorrencia'),
    path('apagar_ocorrencia/<int:utente_id>/<int:ocorrencia_id>', views.apagar_ocorrencia_view, name='apagar_ocorrencia'),
    path('edita_ocorrencia/<int:utente_id>/<int:ocorrencia_id>', views.edita_ocorrencia_view, name='edita_ocorrencia'),
    path('delegacao/', views.delegacao_view, name='delegacao'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='fogot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]
