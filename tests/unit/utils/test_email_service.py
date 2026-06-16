import pytest
from unittest.mock import patch, MagicMock
import os
from src.controle_presenca.utils.email_service import EmailService
from src.controle_presenca.utils.card_generator import gerar_imagem_cartao

# --- TESTES DO EMAIL SERVICE ---
@patch('smtplib.SMTP_SSL')
def test_email_service_send_success(mock_smtp):
    """Testa envio de email com sucesso"""
    # Configura mock do SMTP
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    with patch('src.controle_presenca.config.settings.settings.SMTP_USER', 'test@caaso.org.br'), \
         patch('src.controle_presenca.config.settings.settings.SMTP_PASSWORD', 'password'):
        
        res = EmailService._enviar("dest@email.com", "Assunto", "<html>Corpo</html>")
        assert res is True
        mock_server.login.assert_called_once_with('test@caaso.org.br', 'password')
        mock_server.sendmail.assert_called_once()

@patch('smtplib.SMTP_SSL')
def test_email_service_send_failure(mock_smtp):
    """Testa falha de conexão SMTP"""
    mock_smtp.side_effect = Exception("Conexão falhou")

    with patch('src.controle_presenca.config.settings.settings.SMTP_USER', 'test@caaso.org.br'), \
         patch('src.controle_presenca.config.settings.settings.SMTP_PASSWORD', 'password'):
        
        res = EmailService._enviar("dest@email.com", "Assunto", "<html>Corpo</html>")
        assert res is False

def test_email_service_no_credentials():
    """Testa comportamento caso credenciais SMTP não estejam configuradas"""
    with patch('src.controle_presenca.config.settings.settings.SMTP_USER', None), \
         patch('src.controle_presenca.config.settings.settings.SMTP_PASSWORD', None):
        
        res = EmailService._enviar("dest@email.com", "Assunto", "<html>Corpo</html>")
        assert res is False

@patch('src.controle_presenca.utils.email_service.EmailService._enviar')
def test_enviar_email_templates(mock_enviar):
    """Testa disparo dos templates específicos de email"""
    mock_enviar.return_value = True

    # Aprovação
    from unittest.mock import ANY
    res_ap = EmailService.enviar_email_aprovacao("aluno@email.com", "Joao")
    assert res_ap is True
    mock_enviar.assert_any_call("aluno@email.com", "Aprovação! - Cursinho Popular ExpliCAASO", ANY)

    # Desligamento
    res_des = EmailService.enviar_email_desligamento("aluno@email.com", "Joao")
    assert res_des is True
    mock_enviar.assert_any_call("aluno@email.com", "Desligamento - Cursinho Popular ExpliCAASO", ANY)

    # Cartão
    res_car = EmailService.enviar_email_cartao("aluno@email.com", "Joao", 123456, "caminho/fake.jpg")
    assert res_car is True
    mock_enviar.assert_any_call("aluno@email.com", "Cartão de presença - Cursinho Popular ExpliCAASO", ANY, anexo_path="caminho/fake.jpg")

# --- TESTES DO CARD GENERATOR ---
def test_gerar_imagem_cartao_fallback():
    """Testa geração do cartão (fallback sem Pillow)"""
    output_dir = "tests/unit/utils/temp_cards"
    cartao_id = 987654
    nome = "Aluno Teste"
    
    # Executa a geração com fallback sem Pillow forçado por import mocked
    with patch.dict('sys.modules', {'PIL': None}):
        caminho = gerar_imagem_cartao(cartao_id, nome, output_dir)
        
        assert os.path.exists(caminho)
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            assert str(cartao_id) in conteudo
            assert nome in conteudo
            
    # Limpa arquivo temporário
    if os.path.exists(caminho):
        os.remove(caminho)
    if os.path.exists(output_dir):
        os.rmdir(output_dir)
