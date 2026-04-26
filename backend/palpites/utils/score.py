from django.db.models import F, Func, Sum
from futebol_manager.models import Rodada
from usuarios.models import RodadaModificada

def check_pontuacao(palpites):
    mandante = palpites.filter(golsMandante=F('partida__golsMandante')).count()
    visitante = palpites.filter(golsVisitante=F('partida__golsVisitante')).count()
    vencedor = palpites.filter(vencedor=F('partida__vencedor')).count()
    return mandante+visitante+vencedor

def check_pontuacao_grupo(palpites,grupo):
    rodadas_com_palpites = Rodada.objects.filter(partida__palpite_partida__in=palpites).distinct()
    soma = 0
    for rodada in rodadas_com_palpites:
        rodada_modificada = RodadaModificada.objects.filter(rodada=rodada, grupo=grupo).first()
        if rodada_modificada:
            soma += check_pontuacao(palpites.filter(partida__Rodada=rodada)) * rodada_modificada.modificador
        else:
            soma += check_pontuacao(palpites.filter(partida__Rodada=rodada))

    return soma

def check_pontuacao_jogo(palpite):
    mandante = 1 if palpite.golsMandante == palpite.partida.golsMandante else 0
    visitante = 1 if palpite.golsVisitante == palpite.partida.golsVisitante else 0
    vencedor = 1 if palpite.vencedor == palpite.partida.vencedor else 0
    return mandante + visitante + vencedor

def check_diferenca_gols(palpites):
    pontuacao_usuario = palpites.annotate(
        diferenca_mandante=F('golsMandante') - F('partida__golsMandante'),
        diferenca_visitante=F('golsVisitante') - F('partida__golsVisitante')
    ).annotate(
        diferenca_mandante_abs=Func(F('diferenca_mandante'), function='ABS'),
        diferenca_visitante_abs=Func(F('diferenca_visitante'), function='ABS')
    ).annotate(
        diferenca_total=F('diferenca_mandante_abs') + F('diferenca_visitante_abs')
    ).aggregate(
        pontuacao_total=Sum('diferenca_total')
    )['pontuacao_total']

    return pontuacao_usuario or 0

def check_diferenca_gols_individual(palpite):
    """Retorna a diferença de gols de um único palpite em relação ao resultado real."""
    if palpite.partida.golsMandante == -1:
        return None
    diff_mandante = abs(palpite.golsMandante - palpite.partida.golsMandante)
    diff_visitante = abs(palpite.golsVisitante - palpite.partida.golsVisitante)
    return diff_mandante + diff_visitante