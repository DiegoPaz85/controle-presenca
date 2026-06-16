const API_URL = 'http://localhost:8000';
let currentSection = 'frequencia';

// Exibir alertas
function showGlobalAlert(message, type) {
    const alert = document.getElementById('global-alert');
    alert.textContent = message;
    alert.className = `alert ${type}`;
    alert.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => {
        alert.classList.add('hidden');
    }, 5000);
}

// Inicializar e verificar API
async function inicializar() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const badge = document.getElementById('api-status');
        if (response.ok) {
            badge.innerHTML = '✅ API Online';
            badge.className = 'status-badge online';
            carregarDadosSecao();
        } else {
            throw new Error();
        }
    } catch (e) {
        const badge = document.getElementById('api-status');
        badge.innerHTML = '❌ API Offline';
        badge.className = 'status-badge offline';
    }
}

// Alterar Aba
function switchGestorTab(sectionName) {
    currentSection = sectionName;
    document.querySelectorAll('.gtab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.gestor-section').forEach(sec => sec.classList.add('hidden'));

    document.getElementById(`gtab-${sectionName}`).classList.add('active');
    document.getElementById(`sec-${sectionName}`).classList.remove('hidden');

    carregarDadosSecao();
}

// Carregar dados dependendo da aba ativa
function carregarDadosSecao() {
    if (currentSection === 'frequencia') {
        carregarAlunos();
    } else if (currentSection === 'sgdi') {
        carregarRanking();
    } else if (currentSection === 'auditoria') {
        carregarAuditoria();
    }
}

// ================= ABA 1: DISCENTES & FREQUÊNCIA =================

async function carregarAlunos() {
    const tbody = document.querySelector('#alunos-gestao-table tbody');
    try {
        const response = await fetch(`${API_URL}/alunos/`);
        if (response.ok) {
            const alunos = await response.json();
            if (alunos.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Nenhum discente cadastrado no sistema.</td></tr>`;
                return;
            }

            // Precisamos buscar as métricas de presença na API detalhada ou carregar os valores reais
            // Como a rota de listar_alunos do backend já retorna percentual_presenca e carga_horaria_total,
            // podemos renderizar diretamente.
            // Para isso, vamos obter os dados reais retornados.
            tbody.innerHTML = alunos.map(a => `
                <tr>
                    <td>${a.id}</td>
                    <td><strong>${a.nome}</strong></td>
                    <td>${a.cartao_id}</td>
                    <td><span class="font-bold">${a.percentual_presenca !== undefined ? a.percentual_presenca : 0}%</span></td>
                    <td>${a.carga_horaria_total !== undefined ? a.carga_horaria_total : 0}h</td>
                    <td>
                        <span class="badge ${a.status === 'ATIVADO' ? 'badge-dentro' : 'badge-fora'}">
                            ${a.status}
                        </span>
                    </td>
                    <td>
                        ${a.status === 'ATIVADO' ? 
                            `<button onclick="desativarAluno(${a.id}, '${a.nome}')" class="btn-danger-sm">❌ Desativar</button>` : 
                            `<span class="text-muted">Desativado</span>`
                        }
                    </td>
                </tr>
            `).join('');
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-red">Erro ao carregar lista de alunos.</td></tr>`;
    }
}

async function cadastrarAlunoManual() {
    const nome = document.getElementById('aluno-nome').value.trim();
    const cartao = document.getElementById('aluno-cartao').value.trim();
    const resultDiv = document.getElementById('cadastro-result');

    if (!nome || !cartao) {
        resultDiv.textContent = '⚠️ Preencha todos os campos!';
        resultDiv.className = 'alert error';
        resultDiv.classList.remove('hidden');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/alunos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome, cartao_id: parseInt(cartao) })
        });
        
        const data = await response.json();
        if (response.ok) {
            resultDiv.textContent = `✅ Aluno ${data.nome} cadastrado com sucesso!`;
            resultDiv.className = 'alert success';
            resultDiv.classList.remove('hidden');
            document.getElementById('aluno-nome').value = '';
            document.getElementById('aluno-cartao').value = '';
            carregarAlunos();
        } else {
            resultDiv.textContent = `❌ ${data.detail}`;
            resultDiv.className = 'alert error';
            resultDiv.classList.remove('hidden');
        }
    } catch (e) {
        resultDiv.textContent = '❌ Falha ao conectar com o servidor.';
        resultDiv.className = 'alert error';
        resultDiv.classList.remove('hidden');
    }
}

async function desativarAluno(id, nome) {
    if (!confirm(`Tem certeza que deseja desativar o aluno ${nome}? Ele será excluído logicamente das chamadas.`)) return;

    try {
        const response = await fetch(`${API_URL}/sgdi/alunos/${id}`, { method: 'DELETE' });
        const data = await response.json();
        if (response.ok) {
            showGlobalAlert(`✅ Aluno ${nome} desativado com sucesso.`, 'success');
            carregarAlunos();
        } else {
            showGlobalAlert(`❌ ${data.detail}`, 'error');
        }
    } catch (e) {
        showGlobalAlert("❌ Erro ao desativar aluno.", "error");
    }
}

function exportarRelatorioCSV() {
    window.open(`${API_URL}/alunos/relatorio/csv`, '_blank');
}

// ================= ABA 2: PROCESSO SELETIVO (SGDi) =================

async function carregarRanking() {
    const tbody = document.querySelector('#ranking-table tbody');
    try {
        const response = await fetch(`${API_URL}/sgdi/ranking`);
        if (response.ok) {
            const candidatos = await response.json();
            if (candidatos.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Nenhum candidato pendente no ranking.</td></tr>`;
                return;
            }

            tbody.innerHTML = candidatos.map((c, i) => `
                <tr>
                    <td><strong>${i + 1}º</strong></td>
                    <td>${c.nome}</td>
                    <td>${c.cpf}</td>
                    <td>${c.email}</td>
                    <td><span class="font-bold">${c.pontuacao_socioeconomica}</span> pts</td>
                    <td>
                        <span class="badge badge-warning">${c.status}</span>
                    </td>
                    <td>
                        <button onclick="excluirCandidato(${c.id}, '${c.nome}')" class="btn-danger-sm">Excluir</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-red">Erro ao carregar o ranking.</td></tr>`;
    }
}

async function sincronizarDrive() {
    const spinner = document.getElementById('sync-spinner');
    spinner.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/sgdi/sincronizar-drive`, { method: 'POST' });
        const data = await response.json();
        
        spinner.classList.add('hidden');
        if (response.ok) {
            showGlobalAlert(data.mensagem, 'success');
            carregarRanking();
        } else {
            showGlobalAlert(`❌ ${data.detail}`, 'error');
        }
    } catch (e) {
        spinner.classList.add('hidden');
        showGlobalAlert("❌ Erro ao sincronizar com o Google Drive.", "error");
    }
}

async function executarCorte() {
    const qtdInput = document.getElementById('corte-quantidade');
    const quantidade = parseInt(qtdInput.value.trim());

    if (!quantidade || quantidade < 1) {
        showGlobalAlert("⚠️ Insira uma quantidade válida maior que zero!", "error");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/sgdi/aprovar-corte`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantidade: quantidade })
        });
        
        const data = await response.json();
        if (response.ok) {
            showGlobalAlert(data.mensagem, 'success');
            qtdInput.value = '';
            carregarRanking();
        } else {
            showGlobalAlert(`❌ ${data.detail}`, 'error');
        }
    } catch (e) {
        showGlobalAlert("❌ Erro ao executar linha de corte.", "error");
    }
}

async function efetivarMatricula() {
    const cpfInput = document.getElementById('matricula-cpf');
    const cpf = cpfInput.value.trim();

    if (!cpf) {
        showGlobalAlert("⚠️ Insira o CPF do candidato aprovado!", "error");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/sgdi/matricular`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cpf: cpf })
        });
        
        const data = await response.json();
        if (response.ok) {
            showGlobalAlert(data.mensagem, 'success');
            cpfInput.value = '';
            carregarRanking();
        } else {
            showGlobalAlert(`❌ ${data.detail}`, 'error');
        }
    } catch (e) {
        showGlobalAlert("❌ Erro ao matricular candidato.", "error");
    }
}

async function excluirCandidato(id, nome) {
    if (!confirm(`Tem certeza que deseja excluir permanentemente o candidato ${nome}? Esta ação apagará seus dados de processo seletivo fisicamente.`)) return;

    try {
        const response = await fetch(`${API_URL}/sgdi/candidatos/${id}`, { method: 'DELETE' });
        const data = await response.json();
        if (response.ok) {
            showGlobalAlert(`✅ Candidato ${nome} excluído.`, 'success');
            carregarRanking();
        } else {
            showGlobalAlert(`❌ ${data.detail}`, 'error');
        }
    } catch (e) {
        showGlobalAlert("❌ Erro ao excluir candidato.", "error");
    }
}

// ================= ABA 3: HISTÓRICO & AUDITORIA =================

async function carregarAuditoria() {
    const tbody = document.querySelector('#auditoria-table tbody');
    try {
        const response = await fetch(`${API_URL}/sgdi/historico-geral`);
        if (response.ok) {
            const logs = await response.json();
            if (logs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">Nenhum registro de transação gravado.</td></tr>`;
                return;
            }

            tbody.innerHTML = logs.map(log => {
                const date = new Date(log.data_alteracao).toLocaleString();
                const statusAnt = log.status_anterior ? `<span class="badge badge-neutral">${log.status_anterior}</span>` : '<i>(Início)</i>';
                const statusNovo = `<span class="badge ${
                    log.status_novo === 'confirmado' ? 'badge-dentro' : 
                    log.status_novo === 'aprovado' ? 'badge-aprovado' : 
                    log.status_novo === 'excluido' ? 'badge-fora' : 'badge-neutral'
                }">${log.status_novo}</span>`;
                
                // Trata exibição se discente foi excluído físico
                const nomeDisplay = log.candidato_nome || '<i>(Excluído físico)</i>';
                const cpfDisplay = log.candidato_cpf || '-';

                return `
                    <tr>
                        <td>#${log.id}</td>
                        <td><strong>${nomeDisplay}</strong></td>
                        <td>${cpfDisplay}</td>
                        <td>${statusAnt}</td>
                        <td>${statusNovo}</td>
                        <td>${date}</td>
                        <td><small>${log.observacao || ''}</small></td>
                    </tr>
                `;
            }).join('');
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-red">Erro ao carregar log de auditoria.</td></tr>`;
    }
}

// Atualizar o nome do arquivo selecionado no label
function atualizarNomeArquivoImportado() {
    const fileInput = document.getElementById('local-xlsx-file');
    const label = document.getElementById('label-xlsx-file');
    if (fileInput.files && fileInput.files[0]) {
        label.textContent = `📂 ${fileInput.files[0].name}`;
    } else {
        label.textContent = '📂 Selecionar Planilha';
    }
}

// Importar planilha localmente via API
async function importarPlanilhaLocal() {
    const fileInput = document.getElementById('local-xlsx-file');
    
    if (!fileInput.files || !fileInput.files[0]) {
        showGlobalAlert("⚠️ Por favor, selecione um arquivo de planilha (.xlsx) primeiro!", "error");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_URL}/sgdi/importar`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (response.ok) {
            showGlobalAlert(`✅ Planilha importada! Inseridos: ${data.inseridos}, Erros/Duplicados: ${data.erros}`, 'success');
            fileInput.value = '';
            atualizarNomeArquivoImportado();
            carregarRanking();
        } else {
            showGlobalAlert(`❌ ${data.detail || 'Erro ao processar planilha.'}`, 'error');
        }
    } catch (e) {
        showGlobalAlert("❌ Erro de conexão com o servidor ao importar planilha local.", "error");
    }
}

// Inicializar
inicializar();
