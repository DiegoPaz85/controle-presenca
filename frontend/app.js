const API_URL = 'http://localhost:8000';

// Verificar status da API
async function verificarStatusAPI() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            const statusDiv = document.getElementById('api-status');
            statusDiv.innerHTML = '✅ API Online';
            statusDiv.className = 'status-badge online';
            carregarSessaoAtiva();
            listarAlunos();
        } else {
            throw new Error('API offline');
        }
    } catch (error) {
        const statusDiv = document.getElementById('api-status');
        statusDiv.innerHTML = '❌ API Offline';
        statusDiv.className = 'status-badge offline';
    }
}

// Mostrar alerta
function showAlert(elementId, message, type) {
    const alert = document.getElementById(elementId);
    alert.textContent = message;
    alert.className = `alert ${type}`;
    alert.classList.remove('hidden');
    setTimeout(() => {
        alert.classList.add('hidden');
    }, 5000);
}

// Registrar presença
async function registrarPresenca() {
    const cartaoId = document.getElementById('cartao-id').value;
    if (!cartaoId) {
        showAlert('presenca-result', 'Digite o número do cartão!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/presenca/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cartao_id: cartaoId })
        });

        const data = await response.json();
        if (response.ok) {
            showAlert('presenca-result', `✅ ${data.mensagem}`, 'success');
            document.getElementById('cartao-id').value = '';
        } else {
            showAlert('presenca-result', `❌ ${data.detail}`, 'error');
        }
    } catch (error) {
        showAlert('presenca-result', '❌ Erro ao conectar com a API', 'error');
    }
}

// Carregar sessão ativa
async function carregarSessaoAtiva() {
    try {
        const response = await fetch(`${API_URL}/sessao/ativa`);
        if (response.ok) {
            const data = await response.json();
            const inicio = new Date(data.inicio).toLocaleString();
            document.getElementById('sessao-info').innerHTML = `
                <p><strong>Sessão Ativa:</strong> <span class="ativa">✅ SIM</span></p>
                <p><strong>ID:</strong> ${data.id}</p>
                <p><strong>Início:</strong> ${inicio}</p>
                <p><strong>Status:</strong> ${data.status}</p>
            `;
        } else {
            document.getElementById('sessao-info').innerHTML = `
                <p><strong>Sessão Ativa:</strong> <span class="inativa">❌ NÃO</span></p>
                <p>Nenhuma sessão em andamento.</p>
                <p>Clique em "Iniciar Sessão" para começar.</p>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar sessão:', error);
    }
}

// Iniciar sessão
async function iniciarSessao() {
    try {
        const response = await fetch(`${API_URL}/sessao/iniciar`, { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            showAlert('presenca-result', `✅ Sessão iniciada! ID: ${data.id}`, 'success');
            carregarSessaoAtiva();
        } else {
            showAlert('presenca-result', `❌ ${data.detail}`, 'error');
        }
    } catch (error) {
        showAlert('presenca-result', '❌ Erro ao iniciar sessão', 'error');
    }
}

// Encerrar sessão
async function encerrarSessao() {
    try {
        const response = await fetch(`${API_URL}/sessao/encerrar`, { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            showAlert('presenca-result', `✅ ${data.mensagem}`, 'success');
            carregarSessaoAtiva();
        } else {
            showAlert('presenca-result', `❌ ${data.detail}`, 'error');
        }
    } catch (error) {
        showAlert('presenca-result', '❌ Erro ao encerrar sessão', 'error');
    }
}

// Cadastrar aluno
async function cadastrarAluno() {
    const nome = document.getElementById('aluno-nome').value;
    const cartao = document.getElementById('aluno-cartao').value;

    if (!nome || !cartao) {
        showAlert('aluno-result', 'Preencha todos os campos!', 'error');
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
            showAlert('aluno-result', `✅ Aluno ${data.nome} cadastrado!`, 'success');
            document.getElementById('aluno-nome').value = '';
            document.getElementById('aluno-cartao').value = '';
            listarAlunos();
        } else {
            showAlert('aluno-result', `❌ ${data.detail}`, 'error');
        }
    } catch (error) {
        showAlert('aluno-result', '❌ Erro ao cadastrar aluno', 'error');
    }
}

// Listar alunos
async function listarAlunos() {
    try {
        const response = await fetch(`${API_URL}/alunos/`);
        const alunos = await response.json();
        
        const tbody = document.querySelector('#alunos-table tbody');
        if (alunos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Nenhum aluno cadastrado</td></tr>';
            return;
        }

        tbody.innerHTML = alunos.map(aluno => `
            <tr>
                <td>${aluno.id}</td>
                <td>${aluno.nome}</td>
                <td>${aluno.cartao_id}</td>
                <td><span style="color: ${aluno.status === 'ATIVADO' ? 'green' : 'red'}">${aluno.status}</span></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erro ao listar alunos:', error);
    }
}

// Inicializar
verificarStatusAPI();
setInterval(carregarSessaoAtiva, 10000);
setInterval(listarAlunos, 30000);
