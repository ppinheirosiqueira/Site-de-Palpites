function alternarCamposGeograficos() {
    const escopo = document.getElementById('escopo').value;
    const secaoPais = document.getElementById('secao_pais');
    const secaoContinente = document.getElementById('secao_continente');
    const inputPais = document.getElementById('pais');
    const inputContinente = document.getElementById('continente');

    if (escopo === 'NAC') {
        secaoPais.style.display = 'block';
        inputPais.required = true;
        
        secaoContinente.style.display = 'none';
        inputContinente.required = false;
        inputContinente.value = '';
    } else if (escopo === 'CON') {
        secaoPais.style.display = 'none';
        inputPais.required = false;
        inputPais.value = '';
        
        secaoContinente.style.display = 'block';
        inputContinente.required = true;
    } else { // Mundial
        secaoPais.style.display = 'none';
        inputPais.required = false;
        inputPais.value = '';
        
        secaoContinente.style.display = 'none';
        inputContinente.required = false;
        inputContinente.value = '';
    }
}
    
