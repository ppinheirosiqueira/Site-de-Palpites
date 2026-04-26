from django.db.models import Q

from ..models import Partida

def get_anterior_proximo_partida(partida, variacao): # variacao, se = 0, normal, se > 0, é referente a time, se < 0, é referente ao campeonato
    if variacao == 0:
        partidas = list(Partida.objects.all().order_by('dia'))
    elif variacao > 0:
        partidas = list(Partida.objects.filter(Q(Mandante__id=variacao) | Q(Visitante__id=variacao)).order_by('dia'))
    else:
        partidas = list(Partida.objects.filter(Rodada__edicao_campeonato_id=-variacao).order_by('dia'))

    indice = partidas.index(partida)
    anterior = partidas[indice - 1].id if indice - 1 >= 0 else None
    proximo = partidas[indice + 1].id if indice + 1 < len(partidas) else None

    return anterior, proximo

def definirVencedor(golsMandante, golsVisitante):
    if golsMandante > golsVisitante:
        return 1
    elif golsMandante < golsVisitante:
        return 2
    return 0