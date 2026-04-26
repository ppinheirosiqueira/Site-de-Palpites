from datetime import timedelta
from collections import defaultdict

from django.views.decorators.http import require_POST
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Max

from palpites.utils import ranking, rankingUsuariosNoTime, palpite_da_partida, cravadas
from .utils import classificacao, get_anterior_proximo_partida

from .models import Partida, Continente, TipoTime, Time, EdicaoCampeonato, Rodada, Campeonato
from usuarios.models import User
from palpites.models import Palpite_Partida, Palpite_Campeonato, Medal

def verPartida(request : HttpRequest, id : int, variacao: str = 0) -> HttpResponse:
    if variacao != 0:
        variacao = int(variacao)
    partida = Partida.objects.get(id=id)
    anterior, proximo = get_anterior_proximo_partida(partida, variacao)
    palpites, tam_palpites = palpite_da_partida(partida)
    return render(request, "palpites/partida.html", {
                "title": partida,
                "partida": partida,
                "palpites": palpites,
                "anterior": anterior,
                "proxima": proximo,
                "tamanho_palpites": tam_palpites,
                "variacao": variacao,
                "jogoComecou": timezone.now() >= partida.dia,
    })

def verTimes(request : HttpRequest) -> HttpResponse:
    # 1. A busca eficiente ao banco de dados continua a mesma
    continentes_qs = Continente.objects.prefetch_related('paises__times').order_by('nome')
    
    # 2. Aqui começa a transformação dos dados
    dados_para_template = []
    for continente in continentes_qs:
        selecoes_do_continente = []
        clubes_por_pais = {} # Usaremos um dicionário para agrupar os clubes por país

        for pais in continente.paises.all():
            for time in pais.times.all():
                if time.tipo == TipoTime.SELECAO:
                    selecoes_do_continente.append(time)
                else: # Se não for seleção, é clube
                    # Se for a primeira vez que vemos este país com um clube, criamos a entrada
                    if pais not in clubes_por_pais:
                        clubes_por_pais[pais] = []
                    clubes_por_pais[pais].append(time)
        
        # Apenas adicionamos o continente à lista final se ele tiver alguma seleção OU algum clube
        if selecoes_do_continente or clubes_por_pais:
            dados_para_template.append({
                'continente_obj': continente,
                'selecoes': sorted(selecoes_do_continente, key=lambda t: t.Nome), # Ordena as seleções alfabeticamente
                'paises_com_clubes': sorted(clubes_por_pais.items(), key=lambda item: item[0].nome) # Ordena os países alfabeticamente
            })

    context = {
        'dados_para_template': dados_para_template
    }
    
    return render(request, 'futebol_manager/times.html', context)

def verTime(request : HttpRequest, id : int) -> HttpResponse:
    time = Time.objects.get(id=id)
    fas = User.objects.filter(favorite_team=id)
    jogos = Partida.objects.filter(Mandante=id) | Partida.objects.filter(Visitante=id)
    jogos = jogos.order_by("Rodada__edicao_campeonato", "Rodada__num")

    partidas_por_edicao_campeonato = defaultdict(list)

    for jogo in jogos:
        edicao_campeonato = jogo.Rodada.edicao_campeonato
        partidas_por_edicao_campeonato[edicao_campeonato].append(jogo)

    partidas_por_edicao_campeonato = dict(partidas_por_edicao_campeonato)

    if jogos and Palpite_Partida.objects.filter(partida__in=jogos).count() > 0:
        acertos = rankingUsuariosNoTime(jogos)
    else:
        acertos = None

    return render(request, "futebol_manager/time.html", {
        "time": time,
        "fas": fas,
        "temJogo": jogos.count() > 0,
        "temAcerto": jogos.exclude(golsMandante=-1).count() > 0,
        "jogos": partidas_por_edicao_campeonato,
        "acertos": acertos,
    })

def verCampeonatos(request : HttpRequest) -> HttpResponse:
    edicoes = EdicaoCampeonato.objects.all()
    edicoes_por_campeonato = defaultdict(list)
    for edicao in edicoes:
        edicoes_por_campeonato[edicao.campeonato].append(edicao)

    edicoes_por_campeonato = dict(edicoes_por_campeonato)
    return render(request, "futebol_manager/campeonatos.html", {
        'title': 'Campeonatos',
        'campeonatos': edicoes_por_campeonato    
    })

def verCampeonato(request : HttpRequest, campeonato : int) -> HttpResponse:
    return render(request, "futebol_manager/campeonato.html", {
        'title': Campeonato.objects.get(id=campeonato).nome,
        'edicoes': EdicaoCampeonato.objects.filter(campeonato=campeonato),
    })

def verEdicaoCampeonato(request : HttpRequest, campeonato : int, edicao : int) -> HttpResponse:
    edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,num_edicao=edicao)
    edicoes = EdicaoCampeonato.objects.filter(campeonato=edicao.campeonato)
    cravadasJogadores = cravadas(edicao.id,None)

    rankingJogadores = None
    if edicao.comecou:
        rankingJogadores = ranking(edicao.id,0)
        if rankingJogadores is not None:
            rankingJogadores = list(rankingJogadores)

    campeao = None
    if edicao.terminou:
        top_pontuacao = [(id, pontosP) for _, _, id, pontosP, _ in list(rankingJogadores)[:3]]
        campeao = [{'id': usuario[0],'imagem': User.objects.get(id=usuario[0]).profile_image, 'pontos': usuario[1]} for usuario in top_pontuacao]
    
    if edicao.campeonato.pontosCorridos:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('Rodada').first()
    else:
        paginator = Paginator(Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia'), 10)
        primeiro_jogo_nao_ocorrido = Partida.objects.filter(Rodada__edicao_campeonato=edicao).order_by('dia').first()
        
    if primeiro_jogo_nao_ocorrido:
        jogos_antes = Partida.objects.filter(Rodada__edicao_campeonato=edicao, dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
        pagina_atual = jogos_antes // 10 + 1
    else:
        pagina_atual = paginator.num_pages
        
    page = paginator.get_page(pagina_atual)

    contexto = {
        'edicao': edicao,
        'rodadas': Rodada.objects.filter(edicao_campeonato=edicao).order_by("num"),
        'campeao': campeao,
        'ranking': rankingJogadores,
        "page": page,
        "edicoes": edicoes,
        "cravadas": cravadasJogadores,
    }

    if edicao.campeonato.pontosCorridos:
        ordem = list(range(1, 21))
        temPalpite = False
        classificacaoCampeonato = classificacao(edicao,1,38,0)
        classificacaoCampeonato = zip(ordem,classificacaoCampeonato)
        if len(Palpite_Campeonato.objects.filter(edicao_campeonato=edicao)) > 0:
            temPalpite = True
        contexto['temPalpite'] = temPalpite
        contexto['ordem'] = ordem
        contexto['classificacao'] = classificacaoCampeonato

    return render(request, "futebol_manager/campeonato_edicao.html", contexto)

def verRodada(request : HttpRequest, campeonato : int, edicao : int, rodada : int) -> HttpResponse:
    edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,num_edicao=edicao)
    rodadaAtual = Rodada.objects.get(edicao_campeonato=edicao,num=rodada)
    try:
        anterior = Rodada.objects.get(edicao_campeonato=edicao, num=rodada-1)
    except:
        anterior = None
    try:
        proxima = Rodada.objects.get(edicao_campeonato=edicao, num=rodada+1)
    except:
        proxima = None
    return render(request, "futebol_manager/rodada.html", {
        'edicao': edicao,
        'anterior': anterior,
        'proxima': proxima,
        'partidas': Partida.objects.filter(Rodada=rodadaAtual).order_by('dia'),
        'rodada': rodadaAtual,
    })

# Views de Administração
def register_team(request : HttpRequest) -> HttpResponse:
    message = ""
    if request.method == "POST":
        nome = request.POST["time"]
        escudo = request.POST["escudo"]
        aux = Time(Nome=nome,escudo='media/Escudos/' + escudo)
        aux.save()
        message = f'{nome} registrado com sucesso'
    return render(request, "futebol_manager/register_team.html", {
        "title": "Registrar Time",
        "message": message,
        "edicoes": EdicaoCampeonato.objects.filter(terminou=False),
        "times": Time.objects.all().order_by('Nome'),
    })

def register_tournament(request : HttpRequest) -> HttpResponse:
    message = ""
    if request.method == "POST":
        pontosCorridos = True if request.POST["pontosCorridos"] == "on" else False
        campeonato = Campeonato.objects.get_or_create(nome=request.POST["campeonato"],pontosCorridos=pontosCorridos)[0]
        maiorNum = EdicaoCampeonato.objects.filter(campeonato=campeonato).aggregate(Max('num_edicao'))['num_edicao__max']
        if maiorNum is None:
            maiorNum = 0
        edicao = EdicaoCampeonato.objects.get_or_create(campeonato=campeonato,edicao=request.POST["edicao"],num_edicao=maiorNum+1)[0]
        message = f"{campeonato.nome} - {edicao.edicao} criado com Sucesso"
    return render(request, "futebol_manager/register_tournament.html",{
        "message": message,
        "title": "Registrar Torneio",
    })

@require_POST
def register_team_tournament(request : HttpRequest) -> HttpResponse:
    times = request.POST.getlist('times')
    for time in times:
        quebra = time.split('_')
        campeonato = Campeonato.objects.get(id=quebra[0])
        edicao = EdicaoCampeonato.objects.get(campeonato=campeonato,id=quebra[1])
        auxTime = Time.objects.get(id=quebra[2])
        edicao.times.add(auxTime)
    return redirect(reverse("register_team"))

def register_match(request : HttpRequest) -> HttpResponse:
    message = ""
    if request.method == "POST":
        mandante = int(request.POST["mandante"])
        visitante = int(request.POST["visitante"])

        if mandante == visitante:
            message = "<h3>Não tem como um time jogar contra ele mesmo</h3>"
            return render(request, "futebol_manager/register_match.html", {
                        "message": message,
                        "title": "Registrar Partida",
                        "campeonatos": EdicaoCampeonato.objects.filter(terminou=False),
            })
        
        rodada = request.POST["rodada"]

        if rodada != "0":
            rodada = Rodada.objects.get(id=rodada)
            lista_partidas = Partida.objects.filter(Rodada=rodada)

            for partida in lista_partidas:
                if mandante == partida.Mandante.id or mandante == partida.Visitante.id or visitante == partida.Mandante.id or visitante == partida.Visitante.id:
                    message = "<h3>Não tem como um time fazer dois jogos na mesma rodada</h3>"
                    return render(request, "futebol_manager/register_match.html", {
                            "message": message,
                            "title": "Registrar Partida",
                            "campeonatos": EdicaoCampeonato.objects.filter(terminou=False),
                    })
        else:
            campeonato = int(request.POST["campeonato"])
            rodada = Rodada(num=request.POST["numRodada"],nome=request.POST["nomeRodada"],edicao_campeonato_id=campeonato)
            rodada.save()

        date = request.POST["date"]
        aux = Partida(dia=date,Rodada=rodada,Mandante=Time.objects.get(id=mandante),Visitante=Time.objects.get(id=visitante))
        aux.save()
        message = "<h3>Jogo Salvo com Sucesso</h3>"
    return render(request, "futebol_manager/register_match.html", {
                "message": message,
                "title": "Registrar Partida",
                "campeonatos": EdicaoCampeonato.objects.filter(terminou=False),
    })

def editarPartida(request : HttpRequest) -> HttpResponse:
    return render(request, "futebol_manager/partida_editar.html", {
                "title": "Registrar Partida",
                "partidas": Partida.objects.filter(dia__gt=(timezone.now() - timedelta(days=3))).order_by('dia'),
                "times": Time.objects.all(),
    })

def register_matches(request : HttpRequest) -> HttpResponse:
    return render(request, "futebol_manager/register_json.html", {})

def finalizarCampeonato(request: HttpRequest, edicao:int) -> HttpRequest:
    campeonato = EdicaoCampeonato.objects.get(id=edicao)
    
    rankingJogadores = ranking(edicao,0)
    if rankingJogadores is not None:
        rankingJogadores = list(rankingJogadores)

    top_pontuacao = [(id, pontosP) for _, _, id, pontosP, _ in list(rankingJogadores)[:3]]
    
    for i, jogador in enumerate(top_pontuacao,1):
        aux = Medal(usuario = User.objects.get(id=jogador[0]), edicao_campeonato = campeonato, nivel = i)
        aux.save()
    
    campeonato.terminou = True
    campeonato.save()
    
    url = reverse('edicao', args=(campeonato.campeonato.id,campeonato.num_edicao,))
    return redirect(url)