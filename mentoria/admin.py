from django.contrib import admin
from .models import *
#from app.models import *


# Register your models here.

admin.site.register(AnoLectivo)



# Custom admin for Mentor
class MentorAdmin(admin.ModelAdmin):
    search_fields = ('aluno',)
admin.site.register(Mentor, MentorAdmin)

# Custom admin for Mentorando
class MentorandoAdmin(admin.ModelAdmin):
    search_fields = ('aluno',)
admin.site.register(Mentorando, MentorandoAdmin)

# Custom admin for Mentorando
#class AlunoAdmin(admin.ModelAdmin):
#    search_fields = ('user')
#admin.site.register(Aluno, AlunoAdmin)


class DiadeAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentorando')

admin.site.register(Diade, DiadeAdmin)

class SessaoAdmin(admin.ModelAdmin):
    list_display = ('diade', 'data', 'reportado')
    list_editable = ('reportado', )
    list_filter = ('diade__mentor__aluno',)
    ordering = ['-data']

admin.site.register(Sessao, SessaoAdmin)



