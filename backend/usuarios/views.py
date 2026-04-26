import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.db import IntegrityError

from unidecode import unidecode

from .forms import ProfileImageUpdateForm

from avisos.models import Mensagem
from futebol_manager.models import Time, EdicaoCampeonato, Rodada
from palpites.models import Palpite_Partida, Palpite_Campeonato, Medal
from .models import User, Grupo, RodadaModificada

from palpites.utils import accuracy_user, get_edicoes_usuario, rankingTimesNoPerfil, pontuacao_media, rankingGrupo, cravadas

# Views de Administração de Usuario
def verLogin(request : HttpRequest) -> HttpResponse:
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(reverse("home"))
        else:
            return render(request, "usuarios/login.html", {
                "title": "Login",
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "usuarios/login.html", {
            "title": "Login"
        })

def logout_view(request : HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("home"))

def register(request : HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "usuarios/register.html", {
                "title": "Register",
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "usuarios/register.html", {
                "title": "Register",
                "message": "Username already taken."
            })
        login(request, user)
        return redirect(reverse("home"))
    else:
        return render(request, "usuarios/register.html",{
            "title": "Register"
        })
    
# Views do Usuário
def verUsuario(request : HttpRequest, id : int) -> HttpResponse:
    usuario = User.objects.get(id=id)
    aGm, aGv, aR, aT = accuracy_user(id)
    edicoes = get_edicoes_usuario(id)
    if len(edicoes) > 0:
        media = rankingTimesNoPerfil(id,edicoes[0].id)
    else:
        media = None
    medalhas = Medal.objects.filter(usuario=usuario).order_by("nivel")

    contexto = {
        "title": f"Perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "pontuacao_media": pontuacao_media(id),
        "total_predictions": len(Palpite_Partida.objects.filter(usuario=id)),
        "accuracy_goals_mandante": aGm,
        "accuracy_goals_visitante": aGv,
        "accuracy_result": aR,
        "accuracy_total": aT,
        "media": media,
        "edicoes": edicoes,
        "tem_medalha": len(medalhas),
        "medalhas": medalhas,
    }

    if request.user.id == id:
        formImage = ProfileImageUpdateForm(instance=request.user if request.user.is_authenticated else None)
        contexto['formImage'] = formImage
        contexto['times'] = sorted(Time.objects.all(), key=lambda time: unidecode(time.Nome))
        
    return render(request, "usuarios/usuario.html", contexto)

def editarUsuario(request : HttpRequest, id : int) -> HttpResponse:
    if request.user.id != id:
        return redirect(reverse("home"))

    formImage = ProfileImageUpdateForm(instance=request.user if request.user.is_authenticated else None)
    usuario = User.objects.get(id=id)

    return render(request, "usuarios/usuario_editar.html", {
        "title": f"Editar perfil do Usuário - {usuario.username}",
        "usuario": usuario,
        "form": formImage,
        "times": sorted(Time.objects.all(), key=lambda time: unidecode(time.Nome)),
    })

# Views de Grupo
def verGrupos(request : HttpRequest) -> HttpResponse:
    return render(request, "usuarios/grupos.html",{
        'grupos': Grupo.objects.filter(usuarios=request.user.id),
        'edicoes': EdicaoCampeonato.objects.filter(terminou=False),
    })

def verGrupo(request: HttpRequest, id:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=id)
    
    if not request.user.is_authenticated or not Grupo.objects.filter(usuarios=request.user).filter(id=grupo.id).exists():
        return redirect(reverse("home"))
    
    if  grupo.edicao.comecou:
        rankingJogadores = rankingGrupo(grupo.id)
        if rankingJogadores is not None:
            rankingJogadores = list(rankingJogadores)
    else:
        rankingJogadores = None

    if grupo.edicao.terminou:
        top_pontuacao = [(id, pontosP) for _, _, id, pontosP, _ in list(rankingJogadores)[:3]]
        campeao = [{'id': usuario[0],'imagem': User.objects.get(id=usuario[0]).profile_image, 'pontos': usuario[1]} for usuario in top_pontuacao]
    else:
        campeao = None

    temPalpite = False
    
    for usuario in grupo.usuarios.all():
        if len(Palpite_Campeonato.objects.filter(edicao_campeonato=grupo.edicao,usuario=usuario)) > 0:
            temPalpite = True
            break
    
    cravadasJogadores = cravadas(grupo.edicao.id,grupo.id)
    rodadas = Rodada.objects.filter(edicao_campeonato=grupo.edicao)
    return render(request, "usuarios/grupo.html",{
        'grupo': grupo,
        'dono': grupo.dono == request.user,
        'ranking': rankingJogadores,
        'temPalpite': temPalpite,
        'cravadas': cravadasJogadores,
        'campeao': campeao,
        'rodadas': rodadas,
        'rodadasModificadas': RodadaModificada.objects.filter(rodada__in=rodadas),
        'userList': json.dumps(list(User.objects.all().exclude(id__in=grupo.usuarios.all()).values_list("username",flat=True))),
    })

def sairGrupo(request: HttpRequest, idGrupo:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=idGrupo)
    grupo.usuarios.remove(request.user)

    if len(grupo.usuarios.all()) == 0:
        grupo.delete()
        return redirect(reverse("groups"))
    
    if grupo.dono == request.user:
        grupo.dono = grupo.usuarios.all().order_by('?').first()
    
    grupo.save()

    return redirect(reverse("groups"))

# Views de Atualizar Usuário
def profile(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        form = ProfileImageUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def alterar_cor_grafico(request : HttpRequest, id : int) -> redirect:
    if request.method == 'POST':
        cor = request.POST["cor"]
        if len(cor) == 7:
            user = request.user
            user.corGrafico = cor
            user.save()
    url = reverse('userView', args=(id,))
    return redirect(url)

def mudarTema(request : HttpRequest) -> HttpResponse:
    user = request.user
    
    if not user.is_authenticated:
        return redirect(reverse("home"))

    return render(request, "usuarios/mudar_tema.html", {
        "title": "Mudar Tema",
    })

def aceitarGrupo(request : HttpRequest, idGrupo:int, idUsuario:int, idMensagem:int) -> HttpResponse:
    grupo = Grupo.objects.get(id=idGrupo)
    usuario = User.objects.get(id=idUsuario)
    grupo.usuarios.add(usuario)
    grupo.save()

    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.delete()

    url = reverse('grupo', args=(grupo.id,))
    return redirect(url)

def recusarGrupo(request : HttpRequest, idMensagem:int) -> HttpResponse:
    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.delete()

    return redirect(reverse('mensagens'))