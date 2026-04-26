from django.urls import path
from . import views, api
from django.views.generic.base import RedirectView
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    # ============== Usuario ==============
    path("login", views.verLogin, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("registrar", views.register, name="register"),
    path("usuario/<int:id>", views.verUsuario, name="userView"),
    path("usuario/tema", views.mudarTema, name="mudar_tema"),
    path("atualizar_senha", PasswordChangeView.as_view(), name="change_password"),
    path("usuario/edicao/<int:id>", views.editarUsuario, name="editUserView"),

    # ============== Grupos ==============
    path("grupos", views.verGrupos, name="groups"),
    path("grupo/<int:id>", views.verGrupo, name="grupo"),
    path("sair_grupo/<int:idGrupo>", views.sairGrupo, name="sair_grupo"),
    path("aceitar_grupo/<int:idGrupo>/<int:idUsuario>/<int:idMensagem>", views.aceitarGrupo, name="aceitar_grupo"),
    path("recusar_grupo/<int:idMensagem>", views.recusarGrupo, name="recusar_grupo"),

# =====================================================================================================================
# =============================================== URL de APIs =========================================================
# =====================================================================================================================
    # ============== Usuario ==============
    path("alterar_tema", api.alterar_tema, name="alterar_tema"),
    path("alterar_tema/<int:valor>", api.alterar_tema, name="alterar_tema"),
    path('accounts/password_change_done/', RedirectView.as_view(pattern_name='home'), name='password_change_done'),
    path("alterar_time_favorito", api.alterar_time_favorito, name="alterar_time_favorito"),
    path("alterar_cor_grafico/<int:id>", views.alterar_cor_grafico, name="alterar_cor_grafico"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("attRankingTimes/<int:id>/<int:edicao>", api.attRankingTimes, name="att_ranking_times"),

    # ============== Grupo ==============
    path("create_group/<int:idDono>/<str:nome>/<int:idCampeonato>", api.create_group, name="create_group"),
    path("create_mod/<int:idGrupo>/<int:idRodada>/<str:mod>", api.mod_rodada, name="criar_modificador"),
    path("delete_mod/<int:idModificador>", api.excluir_mod_rodada, name="excluir_modificador"),
    path("convidarPessoa/<int:idGrupo>/<str:nome>", api.criar_convite, name="convidarPessoa"),
]
