from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import Coalesce

from ..models import Partida

def auxRankingClassificacao(edicao):
    partidas = Partida.objects.filter(Rodada__edicao_campeonato=edicao).exclude(golsMandante=-1)

    times = edicao.times.all()
    times_mandante = times.annotate(
        vitorias_mandante=Count('mandante', filter=Q(mandante__in=partidas, mandante__vencedor=1)),
        empates_mandante=Count('mandante', filter=Q(mandante__in=partidas, mandante__vencedor=0)),
        gols_pro_mandante=Coalesce(Sum('mandante__golsMandante', filter=Q(mandante__in=partidas)), Value(0)),
        gols_contra_mandante=Coalesce(Sum('mandante__golsVisitante', filter=Q(mandante__in=partidas)), Value(0)),
    )
    times_visitante = times.annotate(
        vitorias_visitante=Count('visitante', filter=Q(visitante__in=partidas, visitante__vencedor=2)),
        empates_visitante=Count('visitante', filter=Q(visitante__in=partidas, visitante__vencedor=0)),
        gols_pro_visitante=Coalesce(Sum('visitante__golsVisitante', filter=Q(visitante__in=partidas)), Value(0)),
        gols_contra_visitante=Coalesce(Sum('visitante__golsMandante', filter=Q(visitante__in=partidas)), Value(0)),
    )

    estatisticas_times = []

    for time in times:
        time_mandante = times_mandante.get(id=time.id)
        time_visitante = times_visitante.get(id=time.id)

        vitorias = time_mandante.vitorias_mandante + time_visitante.vitorias_visitante
        empates = time_mandante.empates_mandante + time_visitante.empates_visitante
        gols_pro = time_mandante.gols_pro_mandante + time_visitante.gols_pro_visitante
        gols_contra = time_mandante.gols_contra_mandante + time_visitante.gols_contra_visitante
        
        saldo_gols = gols_pro - gols_contra
        pontos = vitorias * 3 + empates

        estatisticas_time = {
            'time': time.Nome,
            'pontos': pontos,
            'vitorias': vitorias,
            'gols_pro': gols_pro,
            'saldo_gols': saldo_gols,
        }

        estatisticas_times.append(estatisticas_time)

    # Ordenar a lista de dicionários com base nos pontos, vitórias, saldo de gols e gols pró
    estatisticas_times.sort(key=lambda x: (-x['pontos'], -x['vitorias'], -x['saldo_gols'], -x['gols_pro']))

    return estatisticas_times

def classificacao(edicao, rodada_inicial, rodada_final, tipoClassificacao):
    partidas = Partida.objects.filter(
        Rodada__edicao_campeonato=edicao,
        Rodada__num__gte=rodada_inicial,
        Rodada__num__lte=rodada_final,
    ).exclude(golsMandante=-1)

    times = edicao.times.all()

    times_mandante = times
    times_visitante = times

    # Calcule as estatísticas para as partidas em casa
    if tipoClassificacao == 0 or tipoClassificacao == 1:
        times_mandante = times.annotate(
            jogos_mandante=Count('mandante', filter=Q(mandante__in=partidas)),
            vitorias_mandante=Count('mandante', filter=Q(mandante__in=partidas, mandante__vencedor=1)),
            empates_mandante=Count('mandante', filter=Q(mandante__in=partidas, mandante__vencedor=0)),
            gols_pro_mandante=Coalesce(Sum('mandante__golsMandante', filter=Q(mandante__in=partidas)), Value(0)),
            gols_contra_mandante=Coalesce(Sum('mandante__golsVisitante', filter=Q(mandante__in=partidas)), Value(0)),
        )

    # Calcule as estatísticas para as partidas fora de casa
    if tipoClassificacao == 0 or tipoClassificacao == 2:
        times_visitante = times.annotate(
            jogos_visitante=Count('visitante', filter=Q(visitante__in=partidas)),
            vitorias_visitante=Count('visitante', filter=Q(visitante__in=partidas, visitante__vencedor=2)),
            empates_visitante=Count('visitante', filter=Q(visitante__in=partidas, visitante__vencedor=0)),
            gols_pro_visitante=Coalesce(Sum('visitante__golsVisitante', filter=Q(visitante__in=partidas)), Value(0)),
            gols_contra_visitante=Coalesce(Sum('visitante__golsMandante', filter=Q(visitante__in=partidas)), Value(0)),
        )

    estatisticas_times = []

    for time in times:
        if tipoClassificacao == 0:
            time_mandante = times_mandante.get(id=time.id)
            time_visitante = times_visitante.get(id=time.id)

            jogos = time_mandante.jogos_mandante + time_visitante.jogos_visitante
            vitorias = time_mandante.vitorias_mandante + time_visitante.vitorias_visitante
            empates = time_mandante.empates_mandante + time_visitante.empates_visitante
            gols_pro = time_mandante.gols_pro_mandante + time_visitante.gols_pro_visitante
            gols_contra = time_mandante.gols_contra_mandante + time_visitante.gols_contra_visitante
        elif tipoClassificacao == 1:
            time_mandante = times_mandante.get(id=time.id)
            jogos = time_mandante.jogos_mandante
            vitorias = time_mandante.vitorias_mandante
            empates = time_mandante.empates_mandante
            gols_pro = time_mandante.gols_pro_mandante
            gols_contra = time_mandante.gols_contra_mandante
        else:
            time_visitante = times_visitante.get(id=time.id)
            jogos = time_visitante.jogos_visitante
            vitorias = time_visitante.vitorias_visitante
            empates = time_visitante.empates_visitante
            gols_pro = time_visitante.gols_pro_visitante
            gols_contra = time_visitante.gols_contra_visitante

        saldo_gols = gols_pro - gols_contra
        pontos = vitorias * 3 + empates
        aproveitamento = (pontos / (jogos * 3)) * 100 if jogos > 0 else 0
        derrotas = jogos - vitorias - empates

        estatisticas_time = {
            'time': time.Nome,
            'pontos': pontos,
            'jogos': jogos,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'saldo_gols': saldo_gols,
            'aproveitamento': aproveitamento,
        }

        estatisticas_times.append(estatisticas_time)

    # Ordenar a lista de dicionários com base nos pontos, vitórias, saldo de gols e gols pró
    estatisticas_times.sort(key=lambda x: (-x['pontos'], -x['vitorias'], -x['saldo_gols'], -x['gols_pro']))

    return estatisticas_times

def modaResultados(edicao):
    jogos = Partida.objects.filter(Rodada__edicao_campeonato__id=edicao).exclude(golsMandante=-1)
    resultados_mais_comuns = jogos.values('golsMandante', 'golsVisitante').annotate(ocorrencias=Count('id')).order_by('-ocorrencias')
    return [[item['ocorrencias'] ,item['golsMandante'], item['golsVisitante']] for item in resultados_mais_comuns]
