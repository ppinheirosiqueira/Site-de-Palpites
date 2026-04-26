from datetime import timedelta

from django.utils import timezone

from ..models import Rodada, EdicaoCampeonato, Partida

def obter_dados_campeonato(id):
    try:
        campeonato = EdicaoCampeonato.objects.get(id=id)
        
        times = campeonato.times.all()
        times_data = [{'id': time.id, 'nome': time.Nome} for time in times]

        rodadas = Rodada.objects.filter(edicao_campeonato=campeonato)
        rodadas_data = [{'id': rodada.id, 'nome': rodada.nome} for rodada in rodadas]

        return times_data, rodadas_data
    except EdicaoCampeonato.DoesNotExist:
        raise Exception('Edição de campeonato não encontrada')
    except Exception as e:
        raise Exception(str(e))
    
def get_edicoes() -> list:
    edicoes = list(EdicaoCampeonato.objects.filter(id__in=Partida.objects.filter(dia__gte=timezone.now() - timedelta(days=90)).values_list("Rodada__edicao_campeonato", flat=True).distinct()))
    ultimo_jogo_ocorrido = Partida.objects.exclude(dia__gt=timezone.now()).order_by('dia').last()
    if ultimo_jogo_ocorrido:
        edicao_ultimo_jogo = EdicaoCampeonato.objects.get(rodada__partida__id=ultimo_jogo_ocorrido.id)
        if edicao_ultimo_jogo in edicoes:
            edicoes.remove(edicao_ultimo_jogo)
        edicoes.insert(0, edicao_ultimo_jogo)
    return edicoes