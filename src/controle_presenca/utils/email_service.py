import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from ..config.settings import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def _enviar(destinatario: str, assunto: str, corpo_html: str, anexo_path: str = None) -> bool:
        """Helper para enviar emails via SMTP"""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("Configurações SMTP ausentes no .env. Email não enviado.")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = settings.SMTP_USER
        msg['To'] = destinatario

        # Adiciona corpo HTML
        msg.attach(MIMEText(corpo_html, 'html'))

        # Se houver anexo, adiciona
        if anexo_path and os.path.exists(anexo_path):
            with open(anexo_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(anexo_path)}'
            )
            msg.attach(part)

        try:
            # Estabelece conexão segura
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, [destinatario], msg.as_string())
            logger.info(f"Email enviado com sucesso para {destinatario}.")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email para {destinatario}: {e}")
            return False

    @classmethod
    def enviar_email_aprovacao(cls, destinatario: str, nome_aluno: str) -> bool:
        link_forms = 'https://docs.google.com/forms/d/e/1FAIpQLSeGp-LHIes1X6sQEkGleJAstSx9VobgG8EC_qZMaHCpX6z5fw/viewform?pli=1'
        link_whatsapp = 'https://chat.whatsapp.com/FvdUCKhJRXkCA6DS5UZe65'
        
        corpo = f"""
        <html>
          <body>
            <h3>Aprovação! - Cursinho Popular ExpliCAASO</h3>
            <p>Parabéns <b>{nome_aluno.upper()}</b>, você foi aprovado para compor a turma 2026-1 do cursinho popular ExpliCAASO!</p>
            <p>Confirme sua inscrição no formulário a seguir: <a href="{link_forms}">Formulário de Confirmação</a></p>
            <p>E entre no grupo de WhatsApp da turma: <a href="{link_whatsapp}">Grupo da Turma (ExpliCAASO 2026)</a></p>
            <br>
            <p>Equipe ExpliCAASO</p>
          </body>
        </html>
        """
        return cls._enviar(destinatario, "Aprovação! - Cursinho Popular ExpliCAASO", corpo)

    @classmethod
    def enviar_email_desligamento(cls, destinatario: str, nome_aluno: str) -> bool:
        corpo = f"""
        <html>
          <body>
            <h3>Notificação de Desligamento</h3>
            <p>Olá <b>{nome_aluno.upper()}</b>,</p>
            <p>Estamos lhe enviando esta mensagem para lhe notificar que você foi desligado(a) do cursinho popular ExpliCAASO.</p>
            <p>Se acredita que isso é um erro, responda a este e-mail ou contate o telefone pedagógico explicando a sua situação.</p>
            <br>
            <p>Atenciosamente,<br>Equipe ExpliCAASO</p>
          </body>
        </html>
        """
        return cls._enviar(destinatario, "Desligamento - Cursinho Popular ExpliCAASO", corpo)

    @classmethod
    def enviar_email_cartao(cls, destinatario: str, nome_aluno: str, cartao_id: int, caminho_imagem: str) -> bool:
        corpo = f"""
        <html>
          <body>
            <h3>Cartão de presença - Cursinho Popular ExpliCAASO</h3>
            <p>Olá <b>{nome_aluno.upper()}</b>,</p>
            <p>Segue o arquivo .jpg do seu novo cartão de identificação do ExpliCAASO, de número <b>{cartao_id}</b>.</p>
            <p>Este cartão é essencial para o registro diário de sua presença nas aulas do cursinho.</p>
            <p>Apresente o QR code contido no cartão ao leitor de códigos USB na sala de aula durante suas saídas e entradas.</p>
            <br>
            <p>Atenciosamente,<br>Equipe ExpliCAASO</p>
          </body>
        </html>
        """
        return cls._enviar(destinatario, "Cartão de presença - Cursinho Popular ExpliCAASO", corpo, anexo_path=caminho_imagem)
