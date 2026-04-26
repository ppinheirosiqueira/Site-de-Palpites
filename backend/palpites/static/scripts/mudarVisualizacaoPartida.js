document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('toggleRanking');
    if (!toggle) return;

    const modoNormal  = document.getElementById('modoNormal');
    const modoRanking = document.getElementById('modoRanking');
    const rankingBody = document.getElementById('rankingBody');

    function buildRankingData() {
        const cards = modoNormal.querySelectorAll('.jogo');
        const rows = [];
        cards.forEach(card => {
            const pontos = parseInt(card.dataset.pontos, 10);
            const diff   = parseInt(card.dataset.diff, 10);
            const nome   = card.querySelector('.player a').textContent.trim();
            const href   = card.querySelector('.player a').getAttribute('href');
            const borderClass = [...card.classList].find(c => c.endsWith('_border')) || '';
            rows.push({ pontos, diff, nome, href, borderClass });
        });
        rows.sort((a, b) => b.pontos - a.pontos || a.diff - b.diff);
        return rows;
    }

    function colorClass(borderClass) {
        if (borderClass === 'green_border')  return 'row-green';
        if (borderClass === 'yellow_border') return 'row-yellow';
        if (borderClass === 'orange_border') return 'row-orange';
        if (borderClass === 'red_border')    return 'row-red';
        return '';
    }

    function renderRanking() {
        const rows = buildRankingData();
        rankingBody.innerHTML = '';
        let posicao = 1;
        rows.forEach((r, i) => {
            const anterior = rows[i - 1];
            if (i > 0 && (r.pontos !== anterior.pontos || r.diff !== anterior.diff)) {
                posicao = i + 1;
            }
            const diffDisplay = r.diff === 9999 ? '—' : r.diff;
            const posDisplay = i > 0 && r.pontos === anterior.pontos && r.diff === anterior.diff ? '-' : `${posicao}º`;
            const tr = document.createElement('tr');
            tr.className = colorClass(r.borderClass);
            tr.innerHTML = `
                <td class="td-pos">${posDisplay}</td>
                <td class="td-nome"><a href="${r.href}">${r.nome}</a></td>
                <td class="td-pts">${r.pontos}</td>
                <td class="td-diff">Δ${diffDisplay}</td>
            `;
            rankingBody.appendChild(tr);
        });
    }

    toggle.addEventListener('change', function () {
        if (this.checked) {
            renderRanking();
            modoNormal.style.display  = 'none';
            modoRanking.style.display = 'block';
        } else {
            modoNormal.style.display  = '';
            modoRanking.style.display = 'none';
        }
    });
});