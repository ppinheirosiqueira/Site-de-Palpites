import os
import importlib.util

from django.http import JsonResponse, HttpRequest
from django.core import serializers
from django.views.decorators.http import require_POST

from .utils import modificador_to_json, get_tema
from palpites.utils import rankingClassicacao, rankingTimesNoPerfil

from avisos.models import Mensagem
from futebol_manager.models import Time, EdicaoCampeonato
from .models import User, Grupo, RodadaModificada

def tema(request : HttpRequest):
    return {'tema': get_tema(request.user)}

def estatisticaRankingClassicacao(request : HttpRequest, idEdicao : int, idGrupo:int = None) -> JsonResponse:
    dados_rankingClassicacao = rankingClassicacao(idEdicao, idGrupo)
    return JsonResponse(dados_rankingClassicacao, safe=False)

@require_POST
def alterar_time_favorito(request : HttpRequest) -> JsonResponse:
    user = request.user
    user.favorite_team = Time.objects.get(id=request.POST["idTime"])
    user.save()
    return JsonResponse({'mensagem': "Time Favorito Atualizado"}, safe=False)

@require_POST
def alterar_tema(request : HttpRequest) -> JsonResponse:
    user = request.user
    if request.POST["tema"] == "default":
        user.corPersonalizada = False    
        user.save()
        return JsonResponse({'mensagem': "Cor atualizada"}, safe=False)

    if request.POST["tema"] == "customizado":
        user.corPersonalizada = True
        user.corFundo = request.POST["fundo"]
        user.corFonte = request.POST["fonte"]
        user.corHover = request.POST["hover"]
        user.corBorda = request.POST["borda"]
        user.corSelecionado = request.POST["selecionado"]
        user.corPontos0 = request.POST["0pontos"]
        user.corPontos1 = request.POST["1pontos"]
        user.corPontos2 = request.POST["2pontos"]
        user.corPontos3 = request.POST["3pontos"]
        user.corFiltro = request.POST["filtro"]
        user.corPersonalizada = True    
        user.save()
        return JsonResponse({'mensagem': "Cor atualizada"}, safe=False)
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    padroes_path = os.path.join(current_dir, "padroes.py")
    spec = importlib.util.spec_from_file_location("padroes", padroes_path)
    padroes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(padroes)
    tema = getattr(padroes, request.POST["tema"])
    user.corPersonalizada = True
    user.corFundo = tema['bg-color']
    user.corFonte = tema['font-color']
    user.corHover = tema['hover-color']
    user.corBorda = tema['border-color']
    user.corSelecionado = tema['selecionado-color']
    user.corPontos0 = tema['pontos-0-color']
    user.corPontos1 = tema['pontos-1-color']
    user.corPontos2 = tema['pontos-2-color']
    user.corPontos3 = tema['pontos-3-color']
    user.corFiltro = tema['filter-color']
    user.save()
    return JsonResponse({'mensagem': "Cor atualizada"}, safe=False)

def attRankingTimes(request: HttpRequest, id:int, edicao:int) -> JsonResponse:
    dados = rankingTimesNoPerfil(id,edicao)
    return JsonResponse({'data': dados}, safe=False)

def create_group(request: HttpRequest, idDono:int, nome:str, idCampeonato:int):
    dono = User.objects.get(id=idDono)
    edicao = EdicaoCampeonato.objects.get(id=idCampeonato)
    
    if len(Grupo.objects.filter(nome=nome,edicao=edicao)) > 0:
        return JsonResponse({'mensagem': "Já existe um grupo com este nome para este campeonato"}, safe=False)
    
    novo_grupo = Grupo(nome=nome,dono=dono,edicao=edicao)
    novo_grupo.save()
    novo_grupo.usuarios.add(dono)
    novo_grupo.save()
    
    grupos = Grupo.objects.filter(usuarios=idDono)
    return JsonResponse({'mensagem': "Grupo Criado com Sucesso", "grupos": serializers.serialize('json', grupos)}, safe=False)

def mod_rodada(request: HttpRequest, idGrupo:int, idRodada:int, mod:str) -> JsonResponse:
    mod_valor = float(mod)
    modificador, criado = RodadaModificada.objects.get_or_create(grupo_id=idGrupo, 
                                                            rodada_id=idRodada,
                                                            defaults={
                                                                'modificador': mod_valor, 
                                                            })
    if not criado:
        modificador.modificador = mod_valor
    modificador.save()
    rodadasModificadas = RodadaModificada.objects.filter(grupo_id=idGrupo).order_by('rodada')
    return JsonResponse({'mensagem': 'Rodada modificada com sucesso', 'rodadasModificadas': [modificador_to_json(modificador) for modificador in rodadasModificadas]}, safe=False)

def excluir_mod_rodada(request: HttpRequest, idModificador:int) -> JsonResponse:
    modificador = RodadaModificada.objects.get(id=idModificador)
    grupo = Grupo.objects.get(id=modificador.grupo.id)
    modificador.delete()
    rodadasModificadas = RodadaModificada.objects.filter(grupo=grupo).order_by('rodada')
    return JsonResponse({'mensagem': 'Modificador Excluído com sucesso', 'rodadasModificadas': [modificador_to_json(modificador) for modificador in rodadasModificadas]}, safe=False)

def criar_convite(request: HttpRequest, idGrupo:int, nome: str) -> JsonResponse:

    try:
        grupo = Grupo.objects.get(id=idGrupo)
        convidado = User.objects.get(username=nome)
        mensagem = Mensagem(to_user=convidado,from_user=grupo.dono,titulo=f"{grupo.dono} te convida para o grupo {grupo.nome}")
        mensagem.save()
        texto = f"<p>O usuário {grupo.dono} te chamou para participar do grupo {grupo.nome} que é referente ao campeonato {grupo.edicao}. Você aceita participar do grupo?</p>"        
        texto += f'<div class="links"><a href="../../aceitar_grupo/{grupo.id}/{convidado.id}/{mensagem.id}"><img src="../../static/icons/aceitar.svg" alt="Aceitar convite" title="Aceitar convite"></a>'
        texto += f'<a href="../../recusar_grupo/{mensagem.id}"><img src="../../static/icons/recusar.svg" alt="recusar convite" title="Recusar convite"></a></div>'
        mensagem.conteudo = texto
        mensagem.save()

        return JsonResponse({'mensagem': 'Jogador convidado com sucesso'}, safe=False)
    except:
        return JsonResponse({'mensagem': 'Algum erro ocorreu ao convidá-lo'}, safe=False)