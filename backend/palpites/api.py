from django.http import JsonResponse, HttpRequest
from django.utils import timezone
from json import dumps, loads
from datetime import datetime, timedelta
from django.core import serializers
from django.core.paginator import Paginator

from futebol_manager.utils import partida_to_json, definirVencedor
from .utils import ranking, rankingClassicacao, check_pontuacao, palpites_campeonato_to_json, cravadas, avgPontos, modaPalpites

from futebol_manager.models import Time, Partida, EdicaoCampeonato, Rodada
from usuarios.models import User, Grupo
from .models import Palpite_Partida, Palpite_Campeonato

def attPalpite(request : HttpRequest, idPartida : int, golsMandante : int, golsVisitante : int) -> JsonResponse:

    partida = Partida.objects.get(id=idPartida)
    if timezone.now() < partida.dia:
        user = request.user

        palpite, criado = Palpite_Partida.objects.get_or_create(usuario=user, 
                                                                partida=partida,
                                                                defaults={
                                                                    'golsMandante': golsMandante, 
                                                                    'golsVisitante': golsVisitante,
                                                                    'vencedor': definirVencedor(golsMandante,golsVisitante)
                                                                })

        if not criado:
            palpite.golsMandante = golsMandante
            palpite.golsVisitante = golsVisitante
            palpite.vencedor = definirVencedor(golsMandante,golsVisitante)
            palpite.save()
            sucesso = "Sucesso - Palpite Alterado"
        else:
            sucesso = "Sucesso - Novo palpite criado"

        return JsonResponse({'mensagem': sucesso})

    return JsonResponse({'mensagem': "Falha ao Palpitar"})

def registroPalpiteEdicao(request : HttpRequest, edicao : int, posicao : int, time : str, pc : str) -> JsonResponse:
    campeonato = EdicaoCampeonato.objects.get(id=edicao)

    if pc == "pc":
        equipe = Time.objects.get(escudo__contains = time)
    else:
        equipe = Time.objects.get(Nome = time)


    if request.user.is_authenticated:
        user = request.user

    try:
        palpite, criado = Palpite_Campeonato.objects.get_or_create(
            usuario=user,
            time=equipe,
            edicao_campeonato=campeonato,
            defaults={'posicao_prevista': posicao}
        )

        if not criado:
            palpite.posicao_prevista = posicao
            palpite.save()
            sucesso = "Sucesso - Palpite Alterado"
        else:
            sucesso = "Sucesso - Novo palpite criado"
    except Exception as e:
        print(f"Falhou: {e}")
        sucesso = "Falhou"

    return JsonResponse({'mensagem': sucesso})

# API HOME
def get_partidas(request : HttpRequest, pagina : int) -> JsonResponse:
    paginator = Paginator(Partida.objects.filter(dia__gt=datetime.now() - timedelta(days=3)).order_by('dia'), 10)
    page_number = request.GET.get('page', pagina)
    page = paginator.get_page(page_number)
    
    partidas = page.object_list
    serialized_partidas = [partida_to_json(partida) for partida in partidas]
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

def get_ranking(request : HttpRequest, edicao : int, rodadaInicial : int, rodadaFinal : int) -> JsonResponse:
    rankingPreenchido = ranking(edicao, int(rodadaInicial), int(rodadaFinal))
    try:
        data_list = [dict(zip(('posicao', 'usernames', 'ids', 'pontosP', 'difGols'), values)) for values in rankingPreenchido]
        json_string = dumps(data_list)
        json_data = loads(json_string)

        return JsonResponse(json_data, safe=False)
    except:
        return JsonResponse({}, safe=False)

# API HOME - GRÁFICO
def att_rodadas(request : HttpRequest, edicao : int) -> JsonResponse:
    data = serializers.serialize('json', Rodada.objects.filter(edicao_campeonato__id=edicao).order_by('num'))
    return JsonResponse(data, safe=False)

def att_usuarios(request: HttpRequest, edicao : int) -> JsonResponse:
    usuariosAux = list(Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=edicao).order_by('usuario__username').values_list("usuario",flat=True).distinct()) 
    usuarios = [User.objects.get(id=usuario).username for usuario in usuariosAux]
    data = {'usuarios': usuarios}
    return JsonResponse(data, safe=False)

def att_grupos(request: HttpRequest, edicao : int) -> JsonResponse:
    grupos = [{'id': grupo.id, 'nome': grupo.nome} for grupo in Grupo.objects.filter(edicao=edicao,usuarios=request.user)]
    data = {'grupos': grupos}
    return JsonResponse(data, safe=False)

def attGrafico(request : HttpRequest, usuarios : str, campeonato : int, rod_Ini : int, rod_Fin : int) -> JsonResponse:
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=campeonato,partida__Rodada__num__gte=rod_Ini, partida__Rodada__num__lte=rod_Fin)
    usernames = []
    if usuarios == "todos":
        usernames = palpites.values_list("usuario__username",flat=True).distinct()
    elif usuarios == "voce":
        usernames.append(request.user.username)
        if usernames[0] == '':
            usernames[0]= palpites.order_by('?').first().usuario.username
    else:
        usernames = usuarios.split("+")

    rodadas = list(range(rod_Ini, rod_Fin + 1))

    grafico = {
        "labels": rodadas,
        "datasets":[]
    }

    for username in usernames:
        pontosP = [check_pontuacao(palpites.filter(partida__Rodada__num=rodada, usuario__username=username)) for rodada in rodadas]
        aux = {
            "label": username,
            "data": pontosP,
            "borderColor": User.objects.get(username=username).corGrafico,
            "fill":False,
        }
        grafico['datasets'].append(aux)

    json_string = dumps(grafico)
    json_data = loads(json_string)

    return JsonResponse(json_data, safe=False)

def attGraficoGrupo(request : HttpRequest, idGrupo : int, rod_Ini : int, rod_Fin : int) -> JsonResponse:
    grupo = Grupo.objects.get(id=idGrupo)
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=grupo.edicao,partida__Rodada__num__gte=rod_Ini, partida__Rodada__num__lte=rod_Fin)
    usernames = [usuario.username for usuario in grupo.usuarios.all()]
    rodadas = list(range(rod_Ini, rod_Fin + 1))
    grafico = {
        "labels": rodadas,
        "datasets":[]
    }
    for username in usernames:
        pontosP = [check_pontuacao(palpites.filter(partida__Rodada__num=rodada, usuario__username=username)) for rodada in rodadas]
        aux = {
            "label": username,
            "data": pontosP,
            "borderColor": User.objects.get(username=username).corGrafico,
            "fill":False,
        }
        grafico['datasets'].append(aux)

    json_string = dumps(grafico)
    json_data = loads(json_string)

    return JsonResponse(json_data, safe=False)

def pegarPalpite(request: HttpRequest, idCampeonato:int, idGrupo:int = None) -> JsonResponse:

    palpites = Palpite_Campeonato.objects.filter(edicao_campeonato=idCampeonato).order_by("usuario", "posicao_prevista")

    if idGrupo:
        palpites = palpites.filter(usuario__in=Grupo.objects.get(id=idGrupo).usuarios.all())

    palpites_agrupados = {}
    for palpite in palpites:
        if palpite.usuario.username not in palpites_agrupados:
            palpites_agrupados[palpite.usuario.username] = []
        palpites_agrupados[palpite.usuario.username].append(palpite)
        
    serialized_times = serializers.serialize('json', Time.objects.all())

    data = {
        'palpites': [palpites_campeonato_to_json(palpites_agrupados,palpite) for palpite in palpites_agrupados],
        'times': serialized_times,
    }

    return JsonResponse(data, safe=False)

# API CAMPEONATO - ESTATISTICAS
def estatisticaCravada(request : HttpRequest, idEdicao : int, idGrupo:int = None) -> JsonResponse:
    dados_cravadas = cravadas(idEdicao, idGrupo)
    return JsonResponse(dados_cravadas, safe=False)

def estatisticaAvgPontos(request : HttpRequest, idEdicao : int, idGrupo:int = None) -> JsonResponse:
    dados_avgPontos = avgPontos(idEdicao, idGrupo)
    return JsonResponse(dados_avgPontos, safe=False)

def estatisticaModaPalpites(request : HttpRequest, idEdicao : int, idGrupo:int = None) -> JsonResponse:
    dados_modaPalpites = modaPalpites(idEdicao, idGrupo)
    return JsonResponse(dados_modaPalpites, safe=False)

def estatisticaRankingClassicacao(request : HttpRequest, idEdicao : int, idGrupo:int = None) -> JsonResponse:
    dados_rankingClassicacao = rankingClassicacao(idEdicao, idGrupo)
    return JsonResponse(dados_rankingClassicacao, safe=False)