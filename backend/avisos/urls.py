from django.urls import path
from . import views, api

urlpatterns = [
    # ============== Mensagens ==============
    path("mensagens", views.mensagens, name="mensagens"),
    path("mensagem/<int:idMensagem>", views.mensagemAberta, name="mensagemAberta"),
    path("mensagemGlobal", views.mensagemGlobal, name="mensagemGlobal"),
    path("processarMensagemGlobal", views.processarMensagemGlobal, name="processarMensagemGlobal"),

# =====================================================================================================================
# =============================================== URL de APIs =========================================================
# =====================================================================================================================

    # ============== Mensagens ==============
    path("marcarNaoLida/<int:idMensagem>", api.marcarNaoLida, name="marcarNaoLida"),
    path("pegarMensagem/<int:idMensagem>", api.pegarMensagem, name="pegarMensagem"),
    path("apagarMensagem/<int:idMensagem>", api.apagarMensagem, name="apagarMensagem"),
]