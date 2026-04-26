from json import dumps, loads
from datetime import datetime

from django.http import JsonResponse, HttpRequest
from django.core.paginator import Paginator
from django.core import serializers
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Max

from .utils import partida_to_json, classificacao, obter_dados_campeonato, modaResultados, definirVencedor

from .models import EdicaoCampeonato, Partida, Time, Rodada, Campeonato

def get_partidas_edicao(request : HttpRequest, edicao : int, pagina : int) -> JsonResponse:
    edicao = EdicaoCampeonato.objects.get(id=edicao)
    if edicao.campeonato.pontosCorridos:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        page = paginator.get_page(pagina)
    else:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia'), 10)
        page = paginator.get_page(pagina)
    
    partidas = page.object_list
    serialized_partidas = [partida_to_json(partida) for partida in partidas]
    serialized_times = serializers.serialize('json', Time.objects.all())
    
    data = {
        'partidas': serialized_partidas,
        'total': page.paginator.num_pages,
        'times': serialized_times,
    }
    
    return JsonResponse(data)

def classificacaoTimesEdicao(request : HttpRequest, edicao : int, rodada_inicial : int, rodada_final : int, tipoClassificacao : int) -> JsonResponse:
    dados = classificacao(EdicaoCampeonato.objects.get(id=edicao), rodada_inicial, rodada_final, tipoClassificacao)
    try:
        json_string = dumps(dados)
        json_data = loads(json_string)

        return JsonResponse(json_data, safe=False)
    except:
        return JsonResponse({}, safe=False)
    
def timesCampeonato(request : HttpRequest, idEdicao : int) -> JsonResponse:
    try:
        times_data, rodadas_data = obter_dados_campeonato(idEdicao)
        return JsonResponse({'times': times_data, 'rodadas': rodadas_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)
    
def estatisticaModaResultados(request : HttpRequest, idEdicao : int) -> JsonResponse:
    dados_modaResultados = modaResultados(idEdicao)
    return JsonResponse(dados_modaResultados, safe=False)

@require_POST
def registrar_rodada_feita(request : HttpRequest) -> JsonResponse:
    dados_json = loads(request.body)
    campeonato = Campeonato.objects.get(nome=dados_json.get('campeonato'))
    edicao_campeonato = EdicaoCampeonato.objects.get(campeonato=campeonato, edicao=dados_json.get('edicao_campeonato'))
    
    rodada = dados_json['rodada']
    rodada_existente = Rodada.objects.filter(edicao_campeonato=edicao_campeonato,nome=rodada).exists()
    if rodada_existente:
        resposta = {'texto': 'Rodada já registrada'}
        return JsonResponse(resposta, safe=False)
    else:
        maior_rodada = edicao_campeonato.rodada_set.aggregate(Max('num'))['num__max']
        if maior_rodada is not None:
            rodada = Rodada.objects.create(nome=rodada,edicao_campeonato=edicao_campeonato,num=maior_rodada+1)
        else:
            rodada = Rodada.objects.create(nome=rodada,edicao_campeonato=edicao_campeonato,num=1)

    jogos = dados_json['jogos']
    formato_original = "%d/%m/%Y %H:%M"
    for jogo in jogos:
        data_convertida = datetime.strptime(jogo['data'], formato_original).strftime("%Y-%m-%d %H:%M:%S")
        aux = Partida(dia=data_convertida,Rodada=rodada,Mandante=Time.objects.get(Nome=jogo['mandante']),Visitante=Time.objects.get(Nome=jogo['visitante']))
        aux.save()

    resposta = {'texto': 'Rodada registrada com sucesso'}
    return JsonResponse(resposta, safe=False)

@require_POST
def att_partida(request):
    if request.user.is_superuser:
        partida = int(request.POST["idPartida"])
        aux = Partida.objects.get(id=partida)
        gMan = request.POST["gMan"]
        gVis = request.POST["gVis"]
        aux.golsMandante = gMan
        aux.golsVisitante = gVis
        message = "Resultado salvo com Sucesso - "
        if gMan == gVis:
            aux.vencedor = 0
            message = message + "Empate"
        elif gMan > gVis:
            aux.vencedor = 1
            message = message + "Vencedor: Mandante"
        else:
            aux.vencedor = 2
            message = message + "Vencedor: Visitante"
        aux.save()
        return JsonResponse({'mensagem': message}, safe=False)
    else:
        return JsonResponse({'mensagem': "How did you make this request?"}, safe=False)

@require_POST
def att_data_partida(request):
    if request.user.is_superuser:
        partida = int(request.POST["idPartida"])
        aux = Partida.objects.get(id=partida)
        data = request.POST["data"]
        aux.dia = data
        aux.save()
        return JsonResponse({'mensagem': "Data Atualizada com Sucesso"}, safe=False)
    else:
        return JsonResponse({'mensagem': "How did you make this request?"}, safe=False)

def attResultado(request : HttpRequest, idPartida : int, golsMandante : int, golsVisitante : int) -> JsonResponse:
    partida = Partida.objects.get(id=idPartida)
    if timezone.now() > partida.dia:
        user = request.user
        if user.is_superuser:
            partida.golsMandante = golsMandante
            partida.golsVisitante = golsVisitante
            partida.vencedor = definirVencedor(golsMandante,golsVisitante)
            partida.save()
            return JsonResponse({'mensagem': "Resultado Atualizado"})

    return JsonResponse({'mensagem': "Resultado Não Atualizado"})