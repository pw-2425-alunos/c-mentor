
from . import views
from django.urls import path, include

urlpatterns = [
    path('diades/', views.diades_view, name='diades'),
    path('mentores/', views.mentores_view, name='mentores'),

    path('mentorandos/', views.mentorandos_view, name='mentorandos'),
    path('remover_mentorando/<int:mentorando_id>', views.remover_mentorando_view, name='remover_mentorando'),
    path('cria_diade/', views.cria_diade_view, name='cria_diade'),
    path('cria_mentorando/', views.cria_mentorando_view, name='cria_mentorando'),
    path('cria_mentor/', views.cria_mentor_view, name='cria_mentor'),
    path('sessoes/<int:mentor_id>/sessoes/<int:mentorando_id>/sessoes/<int:sep>/', views.sessoes_view, name='sessoes'),
    path('criar_sessao/<int:diade_id>', views.criar_sessao_view, name='criar_sessao'),
    path('edita/<int:sessao_id>', views.edita_sessao_view, name='edita'),
    path('apaga/<int:sessao_id>', views.apaga_sessao_view, name='apaga'),
    path('perfil/<int:aluno_id>', views.perfil_view, name='perfil'),
    path('av_mentorando/<int:sessao_id>', views.av_mentorando_view, name='av_mentorando'),
    path('vermais/<int:sessao_id>', views.vermais_view, name='vermais'),
    path('all_sessoes/', views.all_sessoes_view, name='all_sessoes'),
    path('report_sessoes_mentor/<int:aluno_id>', views.reportar_sessoes_mentor_view, name='report_sessoes_mentor'),

    path('report_sessaoR/', views.report_sessaoR_view, name='report_sessaoR'),

    path('por_reportar/', views.sessoes_por_reportar_view, name='por_reportar'),

    path('report_sessao/<int:sessao_id>', views.report_sessao_view, name='report_sessao'),
    path('', views.info_view, name='info'),
    path('mentoria/info/', views.info_view),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('emails/', views.emails_view, name='emails'),


]
