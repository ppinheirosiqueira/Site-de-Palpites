from ..models import Palpite_Partida
from django.db.models.functions import Lower
from .score import check_pontuacao_jogo, check_diferenca_gols_individual

def palpite_da_partida(partida):
    palpites = Palpite_Partida.objects.filter(partida=partida).order_by(Lower("usuario__username"))
    resultados = []
    diffs = []
    for palpite in palpites:
        resultados.append(check_pontuacao_jogo(palpite))
        diffs.append(check_diferenca_gols_individual(palpite))
    return zip(palpites, resultados, diffs), len(palpites)

