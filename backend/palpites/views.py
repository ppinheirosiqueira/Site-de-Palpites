from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from datetime import timedelta
from django.core.paginator import Paginator
from django.utils import timezone
from user_agents import parse

from futebol_manager.utils import get_edicoes, definirVencedor
from .utils import ranking

from futebol_manager.models import Partida, EdicaoCampeonato, Rodada
from .models import Palpite_Partida
from usuarios.models import User, Grupo

# Visão Principal
def home(request : HttpRequest) -> HttpResponse:
    edicoes = get_edicoes()
    rodadas = list(Rodada.objects.filter(edicao_campeonato=edicoes[0]).order_by('num'))        

    paginator = Paginator(Partida.objects.filter(dia__gt=timezone.now() - timedelta(days=3)).order_by('dia'), 10)
    primeiro_jogo_nao_ocorrido = Partida.objects.filter(golsMandante=-1).order_by('dia').first()
    if primeiro_jogo_nao_ocorrido:
        jogos_antes = Partida.objects.filter(dia__gt=timezone.now() - timedelta(days=3), dia__lt=primeiro_jogo_nao_ocorrido.dia).count()
        pagina_atual = jogos_antes // 10 + 1
    else:
        pagina_atual = paginator.num_pages
    page = paginator.get_page(pagina_atual)

    contexto = {
            "title": "Pepe League",
            "page": page,
            "ranking": ranking(edicoes[0].id,0),
            "edicoes": edicoes,
            "rodadas": rodadas,
        }

    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    if (user_agent.is_pc):
        usuariosPalpitaramCampeonatoGraficoInicial = list(Palpite_Partida.objects.filter(partida__Rodada__edicao_campeonato=edicoes[0].id).order_by('usuario__username').values_list("usuario",flat=True).distinct()) 
        contexto['usuarios'] = [User.objects.get(id=usuario).username for usuario in usuariosPalpitaramCampeonatoGraficoInicial]
        contexto['grupos'] = Grupo.objects.filter(edicao=edicoes[0],usuarios=request.user) if request.user.is_authenticated else None

    return render(request, "palpites/home.html", contexto)

# Views padrões
def verPagPalpitar(request : HttpRequest) -> HttpResponse:
    if request.method == "POST":
        for key, value in request.POST.items():
            if value != '':
                if key.startswith('man_'):
                    team_id, partida_id = key.split('_')
                    if (len(Palpite_Partida.objects.filter(usuario=request.user,partida=partida_id))==1):
                        aux = Palpite_Partida.objects.get(usuario=request.user,partida=partida_id) # Se o usuário já palpitou, não vou criar outro palpite para ele
                        aux.golsMandante = int(value)
                    else:
                        aux = Palpite_Partida(usuario=request.user,partida=Partida.objects.get(id=int(partida_id)),golsMandante=int(value))
                if key.startswith('vis_'):
                    team_id, partida_id = key.split('_')
                    aux.golsVisitante = int(value)
                    aux.vencedor = definirVencedor(aux.golsMandante,aux.golsVisitante)
                    aux.save()
    faltantes = Partida.objects.filter(dia__gt=timezone.now())
    feitas = Palpite_Partida.objects.filter(usuario=request.user.id, partida__dia__gt=timezone.now())
    for palpite in feitas:
        if palpite.partida in faltantes:
            faltantes = faltantes.exclude(id=palpite.partida.id)
    return render(request, "palpites/palpitar.html", {
                "title": "Registrar Resultado",
                "partidas_feitas": feitas,
                "partidas_faltantes": faltantes
    })

def verInfo(request : HttpRequest) -> HttpResponse:
    return render(request, "palpites/info.html", {})

def verPalpitarEdicao(request : HttpRequest, edicao : int) -> HttpResponse:
    edicao = EdicaoCampeonato.objects.get(id=edicao)
    if not edicao.comecou:
        times = edicao.times.all()
        times_10_a_frente = list(times)[10:] + [None]*10
        return render(request, "palpites/palpitarEdicao.html", {
            'edicao': edicao,
            'times': list(zip(range(1, 11), times[:10], range(11, 21), times_10_a_frente)),
            'range': range(1,21),
        })
    return redirect(reverse("home"))

# Visões de Erro
def pagina_404(request : HttpRequest, exception ) -> HttpResponse:
    return render(request, 'palpites/404.html', {} , status=404)

def pagina_500(request : HttpRequest) -> HttpResponse:
    return render(request, 'palpites/500.html', {} , status=500)
