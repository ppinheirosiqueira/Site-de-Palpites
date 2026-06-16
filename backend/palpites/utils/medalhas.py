from palpites.models import MedalhaRodada, Palpite_Partida
from django.db.models import Sum, F, Func
from collections import defaultdict
from .score import check_pontuacao_jogo, check_diferenca_gols_individual

def nivel_para_posicao(pos):
    if pos == 1:
        return MedalhaRodada.OURO
    if pos == 2:
        return MedalhaRodada.PRATA
    if pos == 3:
        return MedalhaRodada.BRONZE
    return None

def processar_medalhas_rodada(rodada):
    MedalhaRodada.objects.filter(rodada=rodada).delete()

    palpites = Palpite_Partida.objects.filter(
        partida__Rodada=rodada
    ).select_related('partida')


    scores = defaultdict(lambda: {'pontos': 0, 'diff': 0, 'usuario': None})

    for palpite in palpites:
        uid = palpite.usuario_id
        scores[uid]['usuario'] = palpite.usuario
        scores[uid]['pontos'] += check_pontuacao_jogo(palpite)
        diff = check_diferenca_gols_individual(palpite)
        if diff is not None:
            scores[uid]['diff'] += diff

    if not scores:
        return

    # Ordena por pontos desc, diff asc
    ranking = sorted(scores.values(), key=lambda x: (-x['pontos'], x['diff']))

    proxima_medalha = 0
    for i, jogador in enumerate(ranking):
        eh_empate = i > 0 and jogador['pontos'] == ranking[i-1]['pontos'] and jogador['diff'] == ranking[i-1]['diff']
        
        if not eh_empate:
            proxima_medalha += 1

        if proxima_medalha == 1:
            nivel = MedalhaRodada.OURO
        elif proxima_medalha == 2:
            nivel = MedalhaRodada.PRATA
        elif proxima_medalha == 3:
            nivel = MedalhaRodada.BRONZE
        else:
            break

        MedalhaRodada.objects.create(
            usuario=jogador['usuario'],
            rodada=rodada,
            nivel=nivel
        )
