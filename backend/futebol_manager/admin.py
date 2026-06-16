from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Time)
admin.site.register(Partida)
admin.site.register(Campeonato)
admin.site.register(Rodada)
admin.site.register(Pais)
admin.site.register(Continente)

@admin.register(EdicaoCampeonato)
class TimesNaEdicao(admin.ModelAdmin):
    filter_horizontal = ['times']