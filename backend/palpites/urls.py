from django.urls import path
from . import views, api
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('icons/favicon.ico'))),

# =====================================================================================================================
# ========================================== URL de Views =============================================================
# =====================================================================================================================
    path('', views.home, name="home"),
    
    # ============== Palpitar ==============
    path("palpitar", views.verPagPalpitar, name="palpitar"),
    path("palpitarEdicao/<int:edicao>", views.verPalpitarEdicao, name="palpiteEdicao"),

    # ============== Informaçõpes ==============
    path("info", views.verInfo, name="info"),

# =====================================================================================================================
# =============================================== URL de APIs =========================================================
# =====================================================================================================================
    # ============== Home ==============
    path("ranking/<edicao>/<rodadaInicial>/<rodadaFinal>", api.get_ranking, name="ranking"),
    path("attPagina/<int:pagina>", api.get_partidas, name="att_paginas"),
    # ============== Home - Gráfico ==============
    path("attGrafico/<str:usuarios>/<int:campeonato>/<int:rod_Ini>/<int:rod_Fin>", api.attGrafico, name="attGrafico"),
    path("attGraficoGrupo/<int:idGrupo>/<int:rod_Ini>/<int:rod_Fin>", api.attGraficoGrupo, name="attGraficoGrupo"),
    path("attRodadas/<int:edicao>", api.att_rodadas, name="att_rodadas"),
    path("attUsuarios/<int:edicao>", api.att_usuarios, name="att_usuarios"),
    path("attGrupos/<int:edicao>", api.att_grupos, name="att_grupos"),

    # ============== Campeonatos ==============
    path("registroPalpiteEdicao/<int:edicao>/<int:posicao>/<path:time>/<str:pc>", api.registroPalpiteEdicao, name="registroPalpiteEdicao"),
    path("pegarPalpite/<int:idCampeonato>", api.pegarPalpite, name="pegarPalpites"),
    path("estatistica/<int:idEdicao>/cravadas", api.estatisticaCravada, name="estatisticaCravada"),
    path("estatistica/<int:idEdicao>/avgPontos", api.estatisticaAvgPontos, name="estatisticaAvgPontos"),
    path("estatistica/<int:idEdicao>/modaPalpites", api.estatisticaModaPalpites, name="estatisticaModaPalpites"),
    path("estatistica/<int:idEdicao>/rankingClassicacao", api.estatisticaRankingClassicacao, name="estatisticaRankingClassicacao"),

    # ============== Campeonatos - Filtro de Grupo ==============
    path("pegarPalpite/<int:idCampeonato>/<int:idGrupo>", api.pegarPalpite, name="pegarPalpitesGrupo"),
    path("estatistica/<int:idEdicao>/cravadas/<int:idGrupo>", api.estatisticaCravada, name="estatisticaCravada"),
    path("estatistica/<int:idEdicao>/avgPontos/<int:idGrupo>", api.estatisticaAvgPontos, name="estatisticaAvgPontos"),
    path("estatistica/<int:idEdicao>/modaPalpites/<int:idGrupo>", api.estatisticaModaPalpites, name="estatisticaModaPalpites"),
    path("estatistica/<int:idEdicao>/rankingClassicacao/<int:idGrupo>", api.estatisticaRankingClassicacao, name="estatisticaRankingClassicacao"),

    # ============== Partidas ==============
    path("attPalpite/<int:idPartida>/<int:golsMandante>/<int:golsVisitante>", api.attPalpite, name="attPalpite"),
]