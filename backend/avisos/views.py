from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpRequest, HttpResponse

from .models import Mensagem
from usuarios.models import User

def mensagens(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect(reverse("home"))

    return render(request, "avisos/mensagens.html",{
        'mensagens': Mensagem.objects.filter(to_user=request.user).order_by('-id')
    })

def mensagemAberta(request: HttpRequest, idMensagem:int) -> HttpResponse:
    return render(request, "avisos/mensagem.html",{
        'mensagem': Mensagem.objects.get(id=idMensagem)
    })

def mensagemGlobal(request: HttpRequest) -> HttpResponse:
    return render(request, "avisos/mensagemGlobal.html",{
    })

def processarMensagemGlobal(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        conteudo = request.POST.get('conteudo')

        for user in User.objects.all():
            mensagem = Mensagem(to_user=user,from_user=request.user,titulo=titulo,conteudo=conteudo)
            mensagem.save()
            
    return redirect(reverse("mensagemGlobal"))