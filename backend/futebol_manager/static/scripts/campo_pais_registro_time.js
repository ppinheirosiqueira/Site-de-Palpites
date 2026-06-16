function alternarCamposPais() {
    const tipoSelect = document.getElementById('tipo_time');
    const secaoPais = document.getElementById('secao_novo_pais');
    const inputNomePais = document.getElementById('nome_pais');
    const selectContinente = document.getElementById('continente');

    if (tipoSelect.value === 'SE') {
        // Mostra a seção e torna os campos obrigatórios
        secaoPais.style.display = 'block';
        inputNomePais.required = true;
        selectContinente.required = true;
    } else {
        // Oculta a seção e remove a obrigatoriedade
        secaoPais.style.display = 'none';
        inputNomePais.required = false;
        selectContinente.required = false;
        
        // Limpa os valores caso o usuário desista de criar a seleção
        inputNomePais.value = '';
        selectContinente.value = '';
        document.getElementById('bandeira').value = '';
    }
}
