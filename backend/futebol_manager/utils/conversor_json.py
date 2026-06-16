def partida_to_json(partida):
    return {
        'pk': partida.pk,
        'Mandante_id': partida.Mandante.id,
        'Mandante_nome': partida.Mandante.Nome,
        'Mandante_escudo': partida.Mandante.escudo,
        'Visitante_id': partida.Visitante.id,
        'Visitante_nome': partida.Visitante.Nome,
        'Visitante_escudo': partida.Visitante.escudo,
        'golsMandante': partida.golsMandante,
        'golsVisitante': partida.golsVisitante,
        'Rodada': f'{partida.Rodada.edicao_campeonato.campeonato} - {partida.Rodada.nome}',
    }