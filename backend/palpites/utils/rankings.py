from ..models import Palpite_Partida
from usuarios.models import User, Grupo
from .score import check_diferenca_gols, check_pontuacao, check_pontuacao_grupo

def ranking(edicao, rodadaInicial, rodadaFinal):
    if edicao != 0 and rodadaInicial == rodadaFinal == 0:
        palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao)
    elif edicao != 0 and rodadaInicial == rodadaFinal != 0:
        palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao,partida__Rodada__num=rodadaInicial)
    elif edicao != 0 and rodadaInicial != 0 and rodadaInicial != rodadaFinal:
        palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato__id=edicao,partida__Rodada__num__gte=rodadaInicial, partida__Rodada__num__lte=rodadaFinal)

    pessoas = list(User.objects.order_by('id').filter(id__in=palpites.values_list("usuario", flat=True).distinct()))
    usernames = [pessoa.username for pessoa in pessoas]
    ids = [pessoa.id for pessoa in pessoas]
    pontosP = [check_pontuacao(palpites.filter(usuario=pessoa)) for pessoa in ids]
    difGols = [check_diferenca_gols(palpites.filter(usuario=pessoa).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)) for pessoa in ids]

    if (len(usernames) == 0):
        return None
    tuplas = zip(usernames,ids,pontosP,difGols)
    tuplas_ordenadas = sorted(tuplas, key=lambda x: (-x[2], x[3]))

    usernames, ids, pontosP, difGols = zip(*tuplas_ordenadas)
    posicao = []
    for i, _ in enumerate(usernames, start=1):
        if i > 1 and (pontosP[i - 1] == pontosP[i - 2] and difGols[i - 1] == difGols[i - 2]):
            posicao.append("-")
        else:
            posicao.append(i)

    return zip(posicao,usernames,ids,pontosP,difGols)


def rankingGrupo(grupo):
    palpites = Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=Grupo.objects.get(id=grupo).edicao,usuario__in = list(Grupo.objects.get(id=grupo).usuarios.all())) # Pega o ranking de tudo        
    pessoas = list(User.objects.order_by('id').filter(id__in=palpites.values_list("usuario", flat=True).distinct()))
    usernames = [pessoa.username for pessoa in pessoas]
    ids = [pessoa.id for pessoa in pessoas]
    pontosP = [check_pontuacao_grupo(palpites.filter(usuario=pessoa),grupo) for pessoa in ids]
    difGols = [check_diferenca_gols(palpites.filter(usuario=pessoa).exclude(partida__golsMandante=-1, partida__golsVisitante=-1)) for pessoa in ids]

    if (len(usernames) == 0):
        return None
    tuplas = zip(usernames,ids,pontosP,difGols)
    tuplas_ordenadas = sorted(tuplas, key=lambda x: (-x[2], x[3]))

    usernames, ids, pontosP, difGols = zip(*tuplas_ordenadas)
    posicao = []
    for i, _ in enumerate(usernames, start=1):
        if i > 1 and (pontosP[i - 1] == pontosP[i - 2] and difGols[i - 1] == difGols[i - 2]):
            posicao.append("-")
        else:
            posicao.append(i)

    return zip(posicao,usernames,ids,pontosP,difGols)