from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(RodadaModificada)

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    filter_horizontal = ['usuarios']