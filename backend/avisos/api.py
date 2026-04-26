from django.http import JsonResponse, HttpRequest

from .models import Mensagem
from .utils import titulo_mensagem_to_json, mensagem_to_json

def mensagensNaoLidas(request : HttpRequest):
    mensagemNaoLida = False
    
    if request.user.is_anonymous:
        return {'mensagemNaoLida': mensagemNaoLida}
    
    for mensagem in Mensagem.objects.filter(to_user=request.user):
        if not mensagem.lida:
            mensagemNaoLida = True
            break
    return {'mensagemNaoLida': mensagemNaoLida}

def marcarNaoLida(request : HttpRequest, idMensagem: int) -> JsonResponse:
    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.lida = False
    mensagem.save()
    
    mensagens = [titulo_mensagem_to_json(mensagem) for mensagem in Mensagem.objects.filter(to_user=request.user).order_by('-id')]
    return JsonResponse({'titulos': mensagens})

def pegarMensagem(request : HttpRequest, idMensagem: int) -> JsonResponse:
    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.lida = True
    mensagem.save()
    paraTitulos = [titulo_mensagem_to_json(mensagem) for mensagem in Mensagem.objects.filter(to_user=request.user).order_by('-id')]
    return JsonResponse({'mensagem': mensagem_to_json(mensagem),'titulos': paraTitulos})

def apagarMensagem(request : HttpRequest, idMensagem: int) -> JsonResponse:
    mensagem = Mensagem.objects.get(id=idMensagem)
    mensagem.delete()
    paraTitulos = [titulo_mensagem_to_json(mensagem) for mensagem in Mensagem.objects.filter(to_user=request.user).order_by('-id')]
    return JsonResponse({'titulos': paraTitulos})