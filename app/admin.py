from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Curso)

class DAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ano', 'semestre', 'inscritos')
    ordering = ('ano', 'semestre', 'nome')

admin.site.register(Disciplina, DAdmin)


class TurmaAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'nome', 'lotacao', 'inscritos')

admin.site.register(Turma, TurmaAdmin)


class AlunoAdmin(admin.ModelAdmin):
    list_display = ('get_first_name', 'get_last_name', 'user', 'numero', 'curso', 'ano')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'numero', 'curso__nome')
    list_filter = ('curso',)

    # Mostrar o primeiro nome e permitir ordenar
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'user__first_name'  # Permite ordenar

    # Mostrar o apelido e permitir ordenar
    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'user__last_name'  # Permite ordenar


admin.site.register(Aluno, AlunoAdmin)



