// Variáveis globais
var edicaoEscolhida
var rodadaEscolhida
var sliderMin
var sliderMax
var checkFaixa
var faixaWrapper
var rankingDebounce = null

function fetchRankingDebounced() {
    clearTimeout(rankingDebounce)
    rankingDebounce = setTimeout(fetchRanking, 400)
}


function atualizarTrilha() {
    var min = parseInt(sliderMin.min)
    var max = parseInt(sliderMin.max)
    var valMin = parseInt(sliderMin.value)
    var valMax = parseInt(sliderMax.value)
    var pctMin = ((valMin - min) / (max - min)) * 100
    var pctMax = ((valMax - min) / (max - min)) * 100
    var trilha = document.getElementById("sliderTrilha")
    trilha.style.left  = pctMin + "%"
    trilha.style.width = (pctMax - pctMin) + "%"
}

function atualizarZIndex() {
    var valMin = parseInt(sliderMin.value)
    var valMax = parseInt(sliderMax.value)
    var max    = parseInt(sliderMin.max)
    // Se ambos no máximo, min precisa de z-index maior para poder voltar
    if (valMin === valMax && valMax === max) {
        sliderMin.style.zIndex = 5
        sliderMax.style.zIndex = 4
    } else {
        sliderMin.style.zIndex = 4
        sliderMax.style.zIndex = 5
    }
}

window.addEventListener('load', function() {
    edicaoEscolhida = document.getElementById("edicao")
    rodadaEscolhida = document.getElementById("rodada")
    sliderMin       = document.getElementById("sliderMin")
    sliderMax       = document.getElementById("sliderMax")
    checkFaixa      = document.getElementById("checkFaixa")
    faixaWrapper    = document.getElementById("faixaWrapper")

    rodadaEscolhida.addEventListener('change', fetchRanking)

    atualizarTrilha()
    atualizarZIndex()

    sliderMin.addEventListener('input', function() {
        if (parseInt(sliderMin.value) > parseInt(sliderMax.value))
            sliderMin.value = sliderMax.value
        document.getElementById("labelMin").textContent = nomesRodadas[sliderMin.value]
        atualizarTrilha()
        atualizarZIndex()
        fetchRankingDebounced()
    })

    sliderMax.addEventListener('input', function() {
        if (parseInt(sliderMax.value) < parseInt(sliderMin.value))
            sliderMax.value = sliderMin.value
        document.getElementById("labelMax").textContent = nomesRodadas[sliderMax.value]
        atualizarTrilha()
        atualizarZIndex()
        fetchRankingDebounced()
    })

    checkFaixa.addEventListener('change', function() {
        if (this.checked) {
            rodadaEscolhida.style.display = 'none'
            faixaWrapper.style.display    = 'flex'
        } else {
            rodadaEscolhida.style.display = ''
            faixaWrapper.style.display    = 'none'
        }
        fetchRanking()
    })
})

function mudarCampeonato() {
    var selectedOptionEdicao = edicaoEscolhida.value
    rodadaEscolhida.disabled = true
    rodadaEscolhida.innerHTML = ""

    fetch('attRodadas/' + selectedOptionEdicao)
        .then(r => r.json())
        .then(function(data) {
            var rodadas = JSON.parse(data)

            var optionTodas = document.createElement("option")
            optionTodas.value = 0
            optionTodas.text = "Todas"
            rodadaEscolhida.add(optionTodas)

            // Atualiza o range do slider com as rodadas disponíveis
            var totalRodadas = rodadas.length
            sliderMin.max = totalRodadas
            sliderMax.max = totalRodadas
            sliderMin.value = 1
            sliderMax.value = totalRodadas
            document.getElementById("labelMin").textContent = rodadas[0].fields.nome
            document.getElementById("labelMax").textContent = rodadas[totalRodadas-1].fields.nome
            atualizarTrilha()
            atualizarZIndex() 

            nomesRodadas = ["Todas"]
            rodadas.forEach(function(rodada) {
                var option = document.createElement("option")
                option.value = rodada.fields.num
                option.text  = rodada.fields.nome
                rodadaEscolhida.add(option)
                nomesRodadas.push(rodada.fields.nome)
            })

            rodadaEscolhida.disabled = false
            rodadaEscolhida.value = 0
            fetchRanking()
        })
        .catch(e => console.log('Ocorreu um erro:', e))
}

function fetchRanking() {
    var edicao = edicaoEscolhida.value
    var rodadaInicial, rodadaFinal

    if (checkFaixa.checked) {
        rodadaInicial = sliderMin.value
        rodadaFinal   = sliderMax.value
    } else {
        var rodada = rodadaEscolhida.value
        // rodada 0 = Todas → passa 0/0 e a view interpreta como sem filtro
        rodadaInicial = rodada
        rodadaFinal   = rodada
    }

    fetch(`ranking/${edicao}/${rodadaInicial}/${rodadaFinal}`)
        .then(r => r.json())
        .then(exibirDados)
        .catch(e => console.log('Ocorreu um erro:', e))
}

function cabecalho(){
    return `
    <thead>
        <tr>
            <th>Posição</th>
            <th>Usuário</th>
            <th>Pontuação</th>
            <th>Dif. Gols</th>
        </tr>
    </thead>
    `
}

function exibirDados(data) {
    resultadoDiv = document.getElementsByClassName('ranking')
    if (data.length){
        texto = cabecalho() + "<tbody>"
        data.forEach(function(jogador){
            texto += "<tr><td>"
            if (jogador.posicao == 1){
                texto += "<span class='ouro'>" + jogador.posicao + "</span></td>"
            }
            else if(jogador.posicao == 2){
                texto += "<span class='prata'>" + jogador.posicao + "</span></td>"
            }
            else if(jogador.posicao == 3){
                texto += "<span class='bronze'>" + jogador.posicao + "</span></td>"
            }
            else{
                texto += jogador.posicao + "</td>"
            }
            texto += "<td><a href=usuario/" + jogador.ids + ">" + jogador.usernames + "</a></td><td>" + jogador.pontosP + "</td><td>" + jogador.difGols + "</td></tr>"
        })
        resultadoDiv[0].innerHTML = texto + "</tbody>"
    }
    else{
        resultadoDiv[0].innerHTML = `<td class="erro">Não existe nenhuma pontuação de nenhum usuário no campeonato e rodada especificados</td>`
    }
}
