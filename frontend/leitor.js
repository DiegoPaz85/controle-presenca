const API_URL = 'http://localhost:8000';
let sessaoAtiva = false;
let leiturasRecentes = [];

// ================= ELEMENTOS DA TELA =================
const inputCartao = document.getElementById('input-cartao');
const alertaLeitura = document.getElementById('alerta-leitura');
const statusSessaoBadge = document.getElementById('status-sessao');
const infoSessao = document.getElementById('info-sessao');
const btnIniciar = document.getElementById('btn-iniciar');
const btnEncerrar = document.getElementById('btn-encerrar');
const listaLeituras = document.getElementById('lista-leituras');

// ================= MODO KIOSK (Foco Contínuo) =================
// Garante que se o usuário clicar fora, o input recupera o foco para não perder a leitura
inputCartao.addEventListener('blur', () => {
    setTimeout(() => { if (sessaoAtiva) inputCartao.focus(); }, 100);
});

// Ouve o evento de leitura do código de barras (tecla Enter)
inputCartao.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const cartaoId = inputCartao.value.trim();
        if (cartaoId) registrarPresenca(cartaoId);
    }
});

function mostrarAlerta(mensagem, tipo) {
    alertaLeitura.textContent = mensagem;
    alertaLeitura.className = `alert ${tipo}`;
    alertaLeitura.classList.remove('hidden');
    setTimeout(() => alertaLeitura.classList.add('hidden'), 3000);
}

function registrarNaTimeline(mensagem, tipo) {
    const hora = new Date().toLocaleTimeString();
    const cor = tipo === 'success' ? 'green' : 'red';
    leiturasRecentes.unshift(`<li style="color: ${cor};"><span>${mensagem}</span> <span>${hora}</span></li>`);
    
    // Mantém apenas os 10 mais recentes na tela
    if (leiturasRecentes.length > 10) leiturasRecentes.pop();
    listaLeituras.innerHTML = leiturasRecentes.join('');
}

// ================= ROTAS DE SESSÃO =================

async function checarSessaoAtiva() {
    try {
        const res = await fetch(`${API_URL}/sessao/ativa`);
        if (res.ok) {
            const data = await res.json();
            sessaoAtiva = true;
            statusSessaoBadge.innerHTML = '✅ Aula em Andamento';
            statusSessaoBadge.className = 'status-badge online';
            infoSessao.innerHTML = `Sessão #${data.id} iniciada às ${new Date(data.inicio).toLocaleTimeString()}`;
            
            btnIniciar.classList.add('hidden');
            btnEncerrar.classList.remove('hidden');
            inputCartao.disabled = false;
            inputCartao.focus();
        } else {
            sessaoAtiva = false;
            statusSessaoBadge.innerHTML = '❌ Nenhuma Aula Ativa';
            statusSessaoBadge.className = 'status-badge offline';
            infoSessao.innerHTML = 'Inicie uma aula para liberar o leitor.';
            
            btnIniciar.classList.remove('hidden');
            btnEncerrar.classList.add('hidden');
            inputCartao.disabled = true;
        }
    } catch (e) {
        infoSessao.innerHTML = '⚠️ Erro ao conectar com o servidor.';
    }
}

async function sessaoIniciar() {
    try {
        const res = await fetch(`${API_URL}/sessao/iniciar`, { method: 'POST' });
        if (res.ok) {
            leiturasRecentes = []; // Limpa histórico antigo
            listaLeituras.innerHTML = '<li style="color: #999;">Nova aula iniciada. Aguardando leituras...</li>';
            checarSessaoAtiva();
        } else {
            const data = await res.json();
            alert(`Erro: ${data.detail}`);
        }
    } catch (e) {
        alert('Erro ao iniciar a aula.');
    }
}

async function sessaoEncerrar() {
    if (!confirm('Deseja realmente encerrar a aula atual? As presenças não poderão mais ser registradas.')) return;
    
    try {
        const res = await fetch(`${API_URL}/sessao/encerrar`, { method: 'POST' });
        if (res.ok) {
            checarSessaoAtiva();
        } else {
            const data = await res.json();
            alert(`Erro: ${data.detail}`);
        }
    } catch (e) {
        alert('Erro ao encerrar a aula.');
    }
}

// ================= ROTAS DE PRESENÇA =================

async function registrarPresenca(cartaoId) {
    if (!sessaoAtiva) {
        mostrarAlerta('Abra uma aula primeiro!', 'error');
        inputCartao.value = '';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/presenca/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cartao_id: cartaoId })
        });
        
        const data = await res.json();
        inputCartao.value = ''; // Limpa rápido para a próxima pessoa
        
        if (res.ok) {
            mostrarAlerta(`✅ ${data.mensagem}`, 'success');
            registrarNaTimeline(`✅ ${data.mensagem}`, 'success');
        } else {
            mostrarAlerta(`❌ ${data.detail}`, 'error');
            registrarNaTimeline(`❌ Cartão ${cartaoId}: ${data.detail}`, 'error');
        }
    } catch (e) {
        mostrarAlerta('❌ Erro de conexão ao registrar.', 'error');
        inputCartao.value = '';
    }
}

// Inicializa a página checando se já tem aula rolando
checarSessaoAtiva();
