function showPalpite(){
    const palpite = document.getElementById("palpite")
    palpite.style.display = "flex";
    document.querySelector(".fechar").onclick = function() {
        palpite.style.display = "none";
    };
}

function showResultado(btn) {
    const resultado = document.getElementById("resultado");
    resultado.style.display = "flex";

    const golsMandante = btn.dataset.golsMandante;
    const golsVisitante = btn.dataset.golsVisitante;
    if (golsMandante !== "-1") {
        document.getElementById("golsMandante").value = golsMandante;
    }
    else{
        document.getElementById("golsMandante").value = 0;
    }
    if (golsVisitante !== "-1") {
        document.getElementById("golsVisitante").value = golsVisitante;
    }   
    else{
        document.getElementById("golsVisitante").value = 0;
    }

    document.querySelector(".fechar").onclick = function() {
        resultado.style.display = "none";
    };
}

function modificarPalpite() {
    var golsMandante = document.getElementById('golsMandante').value;
    var golsVisitante = document.getElementById('golsVisitante').value;

    fetch(`/attPalpite/${idPartida}/${golsMandante}/${golsVisitante}`)
        .then(response => {
            return response.json()
        })
        .then(data => {
            alert(data["mensagem"]);
            location.reload();
        })
        .catch(error => {
            console.error('Erro:', error);
        });
}

function modificarResultado(){
    var golsMandante = document.getElementById('golsMandante').value;
    var golsVisitante = document.getElementById('golsVisitante').value;

    fetch(`/attResultado/${idPartida}/${golsMandante}/${golsVisitante}`)
        .then(response => {
            return response.json()
        })
        .then(data => {
            alert(data["mensagem"]);
            location.reload();
        })
        .catch(error => {
            console.error('Erro:', error);
        });
}