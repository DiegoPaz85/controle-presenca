const API_URL = 'http://localhost:8000';

function mostrarAlerta(mensagem, tipo) {
    const alerta = document.getElementById('alerta-global');
    alerta.textContent = mensagem;
    alerta.className = `alert ${tipo}`;
    alerta.style.display = 'block';
    setTimeout(() => { alerta.style.display = 'none'; }, 5000);
}

function mudarAba(aba) {
    document.getElementById('secao-sgdi').style.display = 'none';
    document.getElementById('secao-relatorios').style.display = 'none';
    document.getElementById('secao-alunos').style.display = 'none';
    
    document.getElementById(`secao-${aba}`).style.display = 'block';

    document.getElementById('tab-sgdi').style.opacity = '0.6';
    document.getElementById('tab-relatorios').style.opacity = '0.6';
    document.getElementById('tab-alunos').style.opacity = '0.6';
    
    document.getElementById(`tab-${aba}`).style.opacity = '1';

    if (aba === 'sgdi') sgdiCarregarRanking();
    if (aba === 'relatorios') relatoriosCarregarFrequencia();
    if (aba === 'alunos') alunosCarregarLista();
}

async function checarStatusAPI() {
    try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
            document.getElementById('api-status').innerHTML = '✅ API Online';
            document.getElementById('api-status').className = 'status-badge online';
            sgdiCarregarRanking();
        }
    } catch (e) {
        document.getElementById('api-status').innerHTML = '❌ API Offline';
        document.getElementById('api-status').className = 'status-badge offline';
    }
}

// ================= ABA 1: SGDI =================
async function sgdiSincronizar() {
    mostrarAlerta('Sincronizando com o Google Forms... Aguarde.', 'info');
    try {
        const res = await fetch(`${API_URL}/sgdi/sincronizar-forms`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(`✅ Sucesso! Sincronizado.`, 'success');
            sgdiCarregarRanking();
        } else {
            mostrarAlerta(`❌ Erro: ${data.detail}`, 'error');
        }
    } catch (e) { mostrarAlerta('❌ Erro de comunicação.', 'error'); }
}

async function sgdiFecharTurma() {
    const vagas = document.getElementById('qtd-vagas').value;
    try {
        const res = await fetch(`${API_URL}/sgdi/fechar-turma?vagas=${vagas}`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(`✅ Turma fechada! ${data.vagas_preenchidas} aprovados.`, 'success');
            sgdiCarregarRanking();
        } else {
            mostrarAlerta(`❌ Erro: ${data.detail}`, 'error');
        }
    } catch (e) { mostrarAlerta('❌ Erro ao fechar a turma.', 'error'); }
}

async function sgdiMatricular() {
    const cpf = document.getElementById('cpf-matricula').value.trim();
    if (!cpf) return mostrarAlerta('⚠️ Digite o CPF!', 'error');
    try {
        const res = await fetch(`${API_URL}/sgdi/candidatos/${cpf}/matricular`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(`🚀 ${data.mensagem}`, 'success');
            document.getElementById('cpf-matricula').value = '';
            sgdiCarregarRanking();
        } else {
            mostrarAlerta(`❌ Erro: ${data.detail}`, 'error');
        }
    } catch (e) { mostrarAlerta('❌ Erro de comunicação.', 'error'); }
}

async function sgdiCarregarRanking() {
    const tbody = document.querySelector('#tabela-ranking tbody');
    try {
        const res = await fetch(`${API_URL}/sgdi/ranking`);
        const candidatos = await res.json();
        if (candidatos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum candidato no sistema.</td></tr>';
            return;
        }
        tbody.innerHTML = candidatos.map(c => `
            <tr>
                <td><strong>${c.nome}</strong></td>
                <td>${c.cpf}</td>
                <td><b style="color: #667eea;">${c.pontuacao_socioeconomica} pts</b></td>
                <td><span class="badge ${c.status === 'aprovado' ? 'badge-dentro' : 'badge-warning'}">${c.status.toUpperCase()}</span></td>
                <td><button onclick="excluirCandidato('${c.cpf}', '${c.nome}')" class="btn-danger-sm">Excluir</button></td>
            </tr>
        `).join('');
    } catch (e) { tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red">Erro ao carregar ranking.</td></tr>'; }
}

async function excluirCandidato(cpf, nome) {
    if (!confirm(`Excluir candidato ${nome}?`)) return;
    try {
        const res = await fetch(`${API_URL}/sgdi/candidatos/${cpf}`, { method: 'DELETE' });
        if (res.ok) {
            mostrarAlerta(`✅ Candidato excluído.`, 'success');
            sgdiCarregarRanking();
        }
    } catch (e) {}
}

// ================= ABA 2: RELATÓRIOS (CARTOLA MÁGICA) =================
async function relatoriosCarregarFrequencia() {
    const tbody = document.querySelector('#tabela-frequencia tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center"><span class="spinner"></span> Processando dados...</td></tr>';
    
    try {
        const res = await fetch(`${API_URL}/relatorios/frequencia`);
        
        if (!res.ok) {
            const errData = await res.json();
            tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: red; font-weight: bold;">
                ❌ Erro na API: ${errData.detail || 'Internal Server Error (500)'}
            </td></tr>`;
            return;
        }
        
        const relatorio = await res.json();

        // CHAVES CORRIGIDAS: Exatamente como a sua API envia
        const listaAlunos = relatorio.estatisticas_alunos || [];
        const totalSessoes = relatorio.total_aulas_dadas || 0;

        if (listaAlunos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum dado gerado. Verifique se há aulas registradas.</td></tr>';
            return;
        }

        tbody.innerHTML = listaAlunos.map(a => `
            <tr>
                <td>${a.cartao_id || '-'}</td>
                <td><strong>${a.nome || '-'}</strong></td>
                <td>${a.presencas || 0} de ${totalSessoes}</td>
                <td><b>${a.porcentagem_frequencia !== undefined ? a.porcentagem_frequencia : 0}%</b></td>
                <td>${a.alerta_evasao 
                    ? '<span style="color: red; font-weight: bold;">⚠️ Risco de Evasão</span>' 
                    : '<span style="color: green;">✅ Regular</span>'}
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red">Erro de comunicação com o servidor.</td></tr>'; 
    }
}

// ================= ABA 3: GESTÃO DE ALUNOS =================
async function alunosCarregarLista() {
    const tbody = document.querySelector('#tabela-alunos tbody');
    try {
        const res = await fetch(`${API_URL}/alunos/`);
        const alunos = await res.json();
        if (alunos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum aluno cadastrado no sistema.</td></tr>';
            return;
        }
        // TABELA LIMPA: Só dados reais que a API /alunos/ entrega.
        tbody.innerHTML = alunos.map(a => `
            <tr>
                <td>${a.id}</td>
                <td><strong>${a.nome}</strong></td>
                <td>${a.cartao_id}</td>
                <td><span style="font-weight: bold; color: ${a.status === 'ATIVADO' ? '#28a745' : '#dc3545'};">${a.status}</span></td>
                <td>${a.status === 'ATIVADO' ? `<button onclick="desativarAluno(${a.id}, '${a.nome}')" class="btn-danger-sm">❌ Desativar</button>` : '-'}</td>
            </tr>
        `).join('');
    } catch (e) { tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red">Erro ao carregar alunos.</td></tr>'; }
}

async function alunosCadastrarManual() {
    const nome = document.getElementById('aluno-nome').value.trim();
    const cartao = document.getElementById('aluno-cartao').value.trim();
    if (!nome || !cartao) return mostrarAlerta('⚠️ Preencha nome e cartão!', 'error');

    try {
        const res = await fetch(`${API_URL}/alunos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome, cartao_id: parseInt(cartao) })
        });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(`✅ Aluno cadastrado!`, 'success');
            document.getElementById('aluno-nome').value = '';
            document.getElementById('aluno-cartao').value = '';
            alunosCarregarLista();
        } else {
            mostrarAlerta(`❌ Erro: ${data.detail}`, 'error');
        }
    } catch (e) { mostrarAlerta('❌ Erro de comunicação.', 'error'); }
}

async function desativarAluno(id, nome) {
    if (!confirm(`Tem certeza que deseja desativar o aluno ${nome}?`)) return;
    try {
        // A URL correta é no roteador de alunos, e não sgdi
        const res = await fetch(`${API_URL}/alunos/${id}`, { method: 'DELETE' });
        
        if (res.ok) {
            mostrarAlerta(`✅ Aluno ${nome} desativado com sucesso.`, 'success');
            alunosCarregarLista(); // Atualiza a tabela na mesma hora
        } else {
            const data = await res.json();
            mostrarAlerta(`❌ Erro: ${data.detail}`, 'error');
        }
    } catch (e) { 
        mostrarAlerta("❌ Erro de comunicação com o servidor.", "error"); 
    }
}

checarStatusAPI();
