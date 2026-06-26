function AttPagina(pagina){
    fetch('../../attPaginaEdicao/' + edicaoId + '/' + pagina)
    .then(response => response.json())
    .then(data => {
        atualizarPaginas(data, pagina)
        exibirPartidas(data)
    })
    .catch(error => {
        console.error(error)
    });
}

function atualizarPaginas(data, pagina){
    var pagination = document.getElementsByClassName("pagination")[0]

    pagination.innerHTML = ''

    if (pagina > 1){
        pagination.innerHTML += '<button onclick="AttPagina(' + (pagina - 1) + ')">Voltar</button> '
    }

    pagination.innerHTML += "Página " + pagina + " de " + data.total  

    if (pagina < data.total){
        pagination.innerHTML += ' <button onclick="AttPagina(' + (pagina + 1) + ')">Próxima</button>'
    }
}

function exibirPartidas(dados){
    var partidas = dados.partidas;
    var container = document.getElementsByClassName("container-partidas")[0];
    var texto = '';
    
    partidas.forEach(function(jogo){
        texto += '<div class="partida">';
        texto += '<a href="/partida/-' + edicaoId + "/" + jogo.pk +'">';
        texto += '<span class="texto nomeCampeonato">' + jogo.Rodada + '</span>';
        texto += '<img class="escudo" src="/' + jogo.Mandante_escudo + '" alt="escudo mandante" title="' + jogo.Mandante_nome +'">';
        
        texto += '<span class="texto">';
        if (jogo.golsMandante > -1 ){
            texto += jogo.golsMandante;
        }
        texto += ' X ';
        if (jogo.golsVisitante > -1 ){
            texto += jogo.golsVisitante;
        }
        texto += '</span>';
        texto += '<img class="escudo" src="/' + jogo.Visitante_escudo + '" alt="escudo visitante" title="' + jogo.Visitante_nome +'">';
        texto += '</a>';       
        texto += '</div>';
    });

    container.innerHTML = texto;
}