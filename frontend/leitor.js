const API_URL = 'http://localhost:8000';
let sessaoAtiva = false;
let intervaloAtivo = false;
let currentTab = 'todos';
let alunosData = [];
let recentes = [];

// Elementos
const scanInput = document.getElementById('scan-cartao-id');
const scanResult = document.getElementById('scan-result');
const timelineList = document.getElementById('timeline-leituras');
const apiStatusBadge = document.getElementById('api-status');

// Manter foco automático constante no input para o leitor de código de barras
if (scanInput) {
    scanInput.focus();
    scanInput.addEventListener('blur', () => {
        setTimeout(() => {
            if (sessaoAtiva) scanInput.focus();
        }, 100);
    });
    scanInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            processarLeituraFisica();
        }
    });
}

// Mostrar alerta
function showScanAlert(message, type) {
    scanResult.textContent = message;
    scanResult.className = `alert ${type}`;
    scanResult.classList.remove('hidden');
    setTimeout(() => {
        scanResult.classList.add('hidden');
    }, 4000);
}

// Inicializar e verificar API
async function inicializar() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            apiStatusBadge.innerHTML = '✅ API Online';
            apiStatusBadge.className = 'status-badge online';
            await atualizarDadosSala();
        } else {
            throw new Error();
        }
    } catch (e) {
        apiStatusBadge.innerHTML = '❌ API Offline';
        apiStatusBadge.className = 'status-badge offline';
    }
}

// Atualizar status e carregar mapa da sala
async function atualizarDadosSala() {
    try {
        const response = await fetch(`${API_URL}/sessao/status-presenca`);
        if (response.ok) {
            const data = await response.json();
            alunosData = data.alunos;
            sessaoAtiva = data.sessao_ativa;
            intervaloAtivo = data.intervalo_ativo;

            // Atualiza Widgets
            document.getElementById('stat-total-alunos').textContent = data.total_alunos;
            document.getElementById('stat-presentes').textContent = `${data.presentes_sala} de ${data.total_alunos}`;
            document.getElementById('stat-ocupacao').textContent = `${data.percentual_presentes}%`;
            
            // Status de Sessão
            const statSessao = document.getElementById('stat-sessao-status');
            const btnSession = document.getElementById('btn-session');
            const btnInterval = document.getElementById('btn-interval');

            if (sessaoAtiva) {
                statSessao.textContent = '✅ EM ANDAMENTO';
                statSessao.className = 'status-value text-green';
                btnSession.textContent = '⏹️ Encerrar Aula (Sessão)';
                btnSession.className = 'btn-danger width-100';
                btnInterval.disabled = false;

                if (intervaloAtivo) {
                    statSessao.textContent = '🟢 INTERVALO ATIVO';
                    statSessao.className = 'status-value text-warning';
                    btnInterval.textContent = '🔴 Encerrar Intervalo';
                    btnInterval.className = 'btn-danger width-100';
                } else {
                    btnInterval.textContent = '🟢 Iniciar Intervalo';
                    btnInterval.className = 'btn-warning width-100';
                }
                
                // Força o foco do input caso esteja lendo
                if (scanInput) scanInput.focus();
            } else {
                statSessao.textContent = '❌ FECHADA';
                statSessao.className = 'status-value text-red';
                btnSession.textContent = '▶️ Iniciar Aula (Sessão)';
                btnSession.className = 'btn-success width-100';
                btnInterval.disabled = true;
                btnInterval.textContent = '🟢 Iniciar Intervalo';
                btnInterval.className = 'btn-warning width-100';
            }

            renderMapaAlunos();
        } else {
            // Se der 404/Erro (ex: sem sessão ativa)
            sessaoAtiva = false;
            intervaloAtivo = false;
            renderMapaAlunos();
        }
    } catch (error) {
        console.error("Erro ao obter dados de presença:", error);
    }
}

// Controlar as Tabs
function setTab(tabName) {
    currentTab = tabName;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');
    renderMapaAlunos();
}

// Renderizar Tabela Dentro/Fora
function renderMapaAlunos() {
    const tbody = document.querySelector('#alunos-sala-table tbody');
    
    // Contadores das tabs
    const total = alunosData.length;
    const dentro = alunosData.filter(a => a.localizacao === 'DENTRO DE SALA').length;
    const fora = total - dentro;

    document.getElementById('count-todos').textContent = total;
    document.getElementById('count-dentro').textContent = dentro;
    document.getElementById('count-fora').textContent = fora;

    // Filtra dados da tab
    let filtrados = alunosData;
    if (currentTab === 'dentro') {
        filtrados = alunosData.filter(a => a.localizacao === 'DENTRO DE SALA');
    } else if (currentTab === 'fora') {
        filtrados = alunosData.filter(a => a.localizacao === 'FORA DE SALA');
    }

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">Nenhum discente listado nesta aba.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtrados.map(a => `
        <tr class="${a.localizacao === 'DENTRO DE SALA' ? 'row-dentro' : 'row-fora'}">
            <td><strong>${a.nome}</strong></td>
            <td>${a.cartao_id}</td>
            <td>
                <span class="badge ${a.localizacao === 'DENTRO DE SALA' ? 'badge-dentro' : 'badge-fora'}">
                    ${a.localizacao === 'DENTRO DE SALA' ? '🟢 Sala' : '🔴 Fora'}
                </span>
            </td>
        </tr>
    `).join('');
}

// Processar Leitura do Scanner Físico
async function processarLeituraFisica() {
    const cardId = scanInput.value.trim();
    if (!cardId) return;

    scanInput.value = ''; // Limpa imediatamente para não travar a próxima leitura
    
    if (!sessaoAtiva) {
        showScanAlert("⚠️ Abra a sessão de aula primeiro!", "error");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/presenca/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cartao_id: cardId })
        });

        const data = await response.json();
        if (response.ok) {
            showScanAlert(`✅ ${data.mensagem}`, "success");
            adicionarAoTimeline(data.mensagem, data.tipo);
            await atualizarDadosSala();
        } else {
            showScanAlert(`❌ ${data.detail}`, "error");
        }
    } catch (error) {
        showScanAlert("❌ Falha de comunicação com o servidor.", "error");
    }
}

// Adicionar leitura recente no feed lateral
function adicionarAoTimeline(mensagem, tipo) {
    const hora = new Date().toLocaleTimeString();
    const icone = tipo === 'entrada' ? '🟢' : '🔴';
    recentes.unshift({ icone, mensagem, hora });

    if (recentes.length > 8) recentes.pop(); // Limita a 8 leituras recentes

    timelineList.innerHTML = recentes.map(r => `
        <li>
            <span class="timeline-time">[${r.hora}]</span>
            <span class="timeline-icon">${r.icone}</span>
            <span class="timeline-msg">${r.mensagem}</span>
        </li>
    `).join('');
}

// Lógica de Aula (Iniciar/Encerrar Sessão)
async function toggleSessao() {
    const endpoint = sessaoAtiva ? 'encerrar' : 'iniciar';
    const confMessage = sessaoAtiva ? 'Tem certeza que deseja ENCERRAR a aula? As presenças de todos os alunos ativos serão recalculadas.' : 'Deseja iniciar uma nova aula?';
    
    if (!confirm(confMessage)) return;

    try {
        const response = await fetch(`${API_URL}/sessao/${endpoint}`, { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            showScanAlert(sessaoAtiva ? "⏹️ Sessão encerrada e frequências salvas." : "▶️ Sessão iniciada!", "success");
            if (sessaoAtiva) recentes = []; // Limpa histórico recente ao encerrar
            await atualizarDadosSala();
        } else {
            showScanAlert(`❌ ${data.detail}`, "error");
        }
    } catch (error) {
        showScanAlert("❌ Erro ao gerenciar sessão.", "error");
    }
}

// Lógica de Intervalo (Iniciar/Encerrar)
async function toggleIntervalo() {
    const endpoint = intervaloAtivo ? 'encerrar' : 'iniciar';
    
    try {
        const response = await fetch(`${API_URL}/sessao/intervalo/${endpoint}`, { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            showScanAlert(intervaloAtivo ? "🔴 Intervalo encerrado." : "🟢 Intervalo iniciado. O tempo de aula não será computado aos presentes.", "success");
            await atualizarDadosSala();
        } else {
            showScanAlert(`❌ ${data.detail}`, "error");
        }
    } catch (error) {
        showScanAlert("❌ Erro ao gerenciar intervalo.", "error");
    }
}

// Inicializar
inicializar();
setInterval(inicializar, 6000); // Polling leve a cada 6s para sincronia do mapa
