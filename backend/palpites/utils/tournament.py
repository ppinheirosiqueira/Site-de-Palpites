from collections import defaultdict

from django.db.models import F, Count

from futebol_manager.utils import auxRankingClassificacao

from .score import check_pontuacao_pepe, check_diferenca_gols

from usuarios.models import User, Grupo
from futebol_manager.models import Partida, EdicaoCampeonato
from ..models import Palpite_Partida, Palpite_Campeonato

def get_edicoes_usuario(id:int) -> list:
    palpites = Palpite_Partida.objects.filter(usuario=id)
    edicoes = palpites.values_list("partida__Rodada__edicao_campeonato",flat=True).distinct()
    return EdicaoCampeonato.objects.filter(id__in=edicoes).order_by("campeonato","num_edicao")

def rankingClassicacao(edicao, grupo):
    classificaoTimes = auxRankingClassificacao(EdicaoCampeonato.objects.get(id=edicao))
    palpites = Palpite_Campeonato.objects.filter(edicao_campeonato__id=edicao)
    if grupo:
        palpites = palpites.filter(usuario__in = list(Grupo.objects.get(id=grupo).usuarios.all()))
    pontuacao_usuarios = defaultdict(lambda: {'pontuacao_total': 0, 'pontuacao_especifica': 0})

    for i, item in enumerate(classificaoTimes, 1):
        time = item['time']
        palpitesTime = palpites.filter(time__Nome = time)
        
        for palpite in palpitesTime:
            posicao_prevista = palpite.posicao_prevista
            diferenca_posicao = abs(posicao_prevista - i)
            pontuacao_usuarios[palpite.usuario]['pontuacao_total'] += diferenca_posicao
            if posicao_prevista == i:
                pontuacao_usuarios[palpite.usuario]['pontuacao_especifica'] += 1

    classificacao_usuarios = sorted(pontuacao_usuarios.items(), key=lambda x: (x[1]['pontuacao_total'], -x[1]['pontuacao_especifica']))
    
    posicao = []
    for i, x in enumerate(classificacao_usuarios, start=0):
        if i > 0 and x[1]['pontuacao_total'] == classificacao_usuarios[i - 1][1]['pontuacao_total'] and x[1]['pontuacao_especifica'] == classificacao_usuarios[i - 1][1]['pontuacao_especifica']:
            posicao.append("-")
        else:
            posicao.append(i + 1)

    resultado_final = []
    for i, (usuario, pontuacoes) in enumerate(classificacao_usuarios, start=1):
        posicao_usuario = posicao[i-1]
        id_usuario = usuario.id
        username_usuario = usuario.username
        pontuacao_total = pontuacoes['pontuacao_total']
        pontuacao_especifica = pontuacoes['pontuacao_especifica']
        resultado_final.append([posicao_usuario, id_usuario, username_usuario, pontuacao_total, pontuacao_especifica])

    return resultado_final

def cravadas(edicao,grupo):
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao)
    if grupo:
        palpites = palpites.filter(usuario__in = list(Grupo.objects.get(id=grupo).usuarios.all()))
    palpites_cravados = palpites.filter(
        golsMandante=F('partida__golsMandante'),
        golsVisitante=F('partida__golsVisitante'),
        vencedor=F('partida__vencedor')
    )
    palpites_zerados = palpites.exclude(golsMandante=F('partida__golsMandante')).exclude(golsVisitante=F('partida__golsVisitante')).exclude(vencedor=F('partida__vencedor')).exclude(partida__golsMandante=-1)

    dados_por_usuario = palpites_cravados.values('usuario__id', 'usuario__username').annotate(cravadas=Count('id')).order_by('-cravadas')
    
    for item in dados_por_usuario:
        usuario_id = item['usuario__id']
        palpites_zerados_usuario = palpites_zerados.filter(usuario__id=usuario_id).count()
        item['zerados'] = palpites_zerados_usuario
    
    dados_por_usuario = sorted(dados_por_usuario, key=lambda x: (-x['cravadas'], x['zerados']))
    
    dados = []
    cravadas_anterior = None
    zeradas_anterior = None
    for i, item in enumerate(dados_por_usuario, 1):
        if cravadas_anterior is not None and item['cravadas'] == cravadas_anterior and item['zerados'] == zeradas_anterior:
            ranking_display = '-'
        else:
            ranking_display = i
        dados.append((ranking_display, item['usuario__id'], item['usuario__username'], item['cravadas'], item['zerados']))
        cravadas_anterior = item['cravadas']
        zeradas_anterior = item['zerados']

    return dados

def avgPontos(edicao, grupo):
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)
    if grupo:
        palpites = palpites.filter(usuario__in = list(Grupo.objects.get(id=grupo).usuarios.all()))
    pessoas = list(User.objects.order_by('id').filter(id__in=palpites.values_list("usuario", flat=True).distinct()))
    usernames = [pessoa.username for pessoa in pessoas]
    ids = [pessoa.id for pessoa in pessoas]
    pontosP = [check_pontuacao_pepe(palpites.filter(usuario=pessoa))/palpites.filter(usuario=pessoa).count() for pessoa in ids]
    difGols = [check_diferenca_gols(palpites.filter(usuario=pessoa))/palpites.filter(usuario=pessoa).count() for pessoa in ids]

    if (len(usernames) == 0):
        return None
    tuplas = zip(usernames,ids,pontosP,difGols)
    tuplas_ordenadas = sorted(tuplas, key=lambda x: (-x[2], x[3]))

    usernames, ids, pontosP, difGols = zip(*tuplas_ordenadas)
    posicao = []
    for i, _ in enumerate(usernames, start=0):
        if i < len(usernames) and (pontosP[i] == pontosP[i - 1] and difGols[i] == difGols[i - 1]):
            posicao.append("-")
        else:
            posicao.append(i+1)

    return [[posicao[i], ids[i], usernames[i], pontosP[i], difGols[i]] for i in range(len(posicao))]

def modaPalpites(edicao, grupo):
    jogos = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao)
    if grupo:
        jogos = jogos.filter(usuario__in = list(Grupo.objects.get(id=grupo).usuarios.all()))
    resultados_mais_comuns = jogos.values('golsMandante', 'golsVisitante').annotate(ocorrencias=Count('id')).order_by('-ocorrencias')
    return [[item['ocorrencias'] ,item['golsMandante'], item['golsVisitante']] for item in resultados_mais_comuns]
