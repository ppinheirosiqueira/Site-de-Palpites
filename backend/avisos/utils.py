
def titulo_mensagem_to_json(mensagem):
    return {
        'idMensagem': mensagem.id,
        'titulo': mensagem.titulo,
        'lida': mensagem.lida,
        'idFrom': mensagem.from_user.id,
        'from': mensagem.from_user.username
    }
    
def mensagem_to_json(mensagem):
    return {
        'idMensagem': mensagem.id,
        'titulo': mensagem.titulo,
        'idFrom': mensagem.from_user.id,
        'from': mensagem.from_user.username,
        'texto': mensagem.conteudo
    }