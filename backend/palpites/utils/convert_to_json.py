def palpites_campeonato_to_json(palpites,palpitador):    
    return {
        'nome': palpitador,
        'palpites': [palpite_campeonato_to_json(palpite) for palpite in palpites[palpitador]]
    }

def palpite_campeonato_to_json(palpite):
    return {
        'time': palpite.time.id,
        'posicao': palpite.posicao_prevista,
    }