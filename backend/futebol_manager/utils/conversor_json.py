def partida_to_json(partida):
    return {
        'pk': partida.pk,
        'Mandante': partida.Mandante.id,
        'Visitante': partida.Visitante.id,
        'golsMandante': partida.golsMandante,
        'golsVisitante': partida.golsVisitante,
        'Rodada': f'{partida.Rodada.edicao_campeonato.campeonato} - {partida.Rodada.nome}',
    }