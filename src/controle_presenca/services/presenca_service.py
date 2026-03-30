from sqlalchemy.orm import Session
from ..database.repositories.presenca_repos import RepositoriosPresenca

class PresencaService:
    def __init__(self, db: Session):
        self.repo = RepositoriosPresenca(db)

    def processar_leitura(self, cartao_id: str):
        try:
            cartao_id_int = int(cartao_id)
        except ValueError:
            return False, "⚠️ ID do cartão deve ser numérico."

        # 1. Verifica sessão ativa
        sessao = self.repo.obter_sessao_ativa()
        if not sessao:
            return False, "⚠️ Nenhuma aula ativa! Inicie uma sessão primeiro."

        # 2. Verifica o aluno
        aluno = self.repo.buscar_aluno(cartao_id_int)
        if not aluno:
            return False, f"❌ Cartão {cartao_id} não cadastrado."
        if aluno.status != 'ATIVADO':
            return False, f"⚠️ Aluno {aluno.nome} está inativo."

        # 3. Define se é entrada ou saída
        ultimo = self.repo.obter_ultimo_registro(aluno.id, sessao.id)
        tipo = 'saida' if (ultimo and ultimo.tipo == 'entrada') else 'entrada'

        # 4. Grava no banco
        self.repo.registrar_ponto(aluno.id, sessao.id, tipo)
        
        acao = "🟢 ENTRADA" if tipo == 'entrada' else "🔴 SAÍDA"
        return True, f"{acao} de {aluno.nome} registrada com sucesso!"
