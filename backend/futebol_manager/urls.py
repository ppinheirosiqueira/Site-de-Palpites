from django.urls import path
from . import views, api

urlpatterns = [
    # ============== Campeonatos ==============
    path("campeonato", views.verCampeonatos, name="campeonatos"),
    path("campeonato/<int:campeonato>", views.verCampeonato, name="campeonato"),
    path("campeonato/<int:campeonato>/<int:edicao>", views.verEdicaoCampeonato, name="edicao"),    
    path("campeonato/<int:campeonato>/<int:edicao>/<int:rodada>", views.verRodada, name="rodada"),
    path("register_tournament", views.register_tournament, name="register_tournament"),
    path("register_team_tournament", views.register_team_tournament, name="register_team_tournament"),
    path("finalizarCampeonato/<int:edicao>", views.finalizarCampeonato, name="finalizarCampeonato"),

    # ============== Times ==============
    path("times", views.verTimes, name="show_teams"),
    path("time/<int:id>", views.verTime, name="show_team"),
    path("registrar_time", views.register_team, name="register_team"),

    # ============== Partidas ==============
    path("partida/<int:id>", views.verPartida, name="partida"),
    path("partida/<str:variacao>/<int:id>", views.verPartida, name="partida_variacao"),
    path("registrar_partida", views.register_match, name="register_match"),
    path("atualizar_partida", views.editarPartida, name="change_match"),
    path("registrar_partidas", views.register_matches, name="register_matches"),

# =====================================================================================================================
# =============================================== URL de APIs =========================================================
# =====================================================================================================================

    # ============== Campeonatos ==============
    path("attPaginaEdicao/<int:edicao>/<int:pagina>", api.get_partidas_edicao, name="att_paginas_edicao"),
    path("classificacao/<int:edicao>/<int:rodada_inicial>/<int:rodada_final>/<int:tipoClassificacao>", api.classificacaoTimesEdicao, name="classificacao"),
    path("timesCampeonato/<int:idEdicao>", api.timesCampeonato, name="timesCampeonato"),
    path("estatistica/<int:idEdicao>/modaResultados", api.estatisticaModaResultados, name="estatisticaModaResultados"),

    # ============== Campeonatos - Filtro der Grupo ==============
    path("estatistica/<int:idEdicao>/modaResultados/<int:idGrupo>", api.estatisticaModaResultados, name="estatisticaModaResultados"),

    # ============== Partidas ==============
    path("registrar_rodada_feita", api.registrar_rodada_feita, name="registrar_rodada_feita"),
    path("attResultado/<int:idPartida>/<int:golsMandante>/<int:golsVisitante>", api.attResultado, name="attResultado"),
    path("att_partida", api.att_partida, name="attPartida"),
    path("att_data_partida", api.att_data_partida, name="attDataPartida"),

]