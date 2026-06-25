import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw, ImageFont


class EmailService:
    def __init__(self):
        self.remetente = os.getenv("EMAIL_REMETENTE")
        self.senha = os.getenv("EMAIL_SENHA_APP")

        if not self.remetente or not self.senha:
            print(
                "⚠️ Aviso: Credenciais de e-mail não configuradas no .env. E-mails não serão enviados."
            )

    def _gerar_imagem_cartao(self, nome_aluno: str, cartao_id: int) -> str:
        """
        Desenha um cartão provisório no estilo USP/CAASO e salva como JPG.
        Retorna o caminho temporário do arquivo gerado.
        """
        # Cria uma imagem base de 600x350 pixels com fundo branco
        img = Image.new("RGB", (600, 350), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Paleta de Cores (Verde e Amarelo USP)
        verde_usp = (0, 112, 54)
        amarelo_usp = (255, 204, 0)
        preto = (30, 30, 30)

        # Faixa superior verde (Cabeçalho)
        draw.rectangle([0, 0, 600, 80], fill=verde_usp)
        # Linha fina amarela embaixo da verde
        draw.rectangle([0, 80, 600, 90], fill=amarelo_usp)

        # Tenta usar uma fonte padrão. O default do PIL é pequeno, mas funciona como placeholder.
        # (A equipe pode colocar um arquivo .ttf na pasta depois e alterar aqui)
        fonte_padrao = ImageFont.load_default()

        # Textos do Cabeçalho
        draw.text(
            (20, 30),
            "CURSINHO EXPLICAASO - CAMPUS SAO CARLOS",
            fill=(255, 255, 255),
            font=fonte_padrao,
        )

        # Dados do Aluno
        draw.text((20, 130), "NOME DO ALUNO(A):", fill=preto, font=fonte_padrao)
        draw.text(
            (20, 150), nome_aluno.upper()[:35], fill=verde_usp, font=fonte_padrao
        )  # Limita a 35 letras

        draw.text(
            (20, 210), "Nº DE INSCRICAO (CARTAO ID):", fill=preto, font=fonte_padrao
        )
        draw.text((20, 230), str(cartao_id), fill=preto, font=fonte_padrao)

        draw.text(
            (20, 310),
            "DOCUMENTO PROVISORIO - VALIDO PARA ACESSO AS AULAS",
            fill=(100, 100, 100),
            font=fonte_padrao,
        )

        # Quadrado pontilhado/linha simulando o espaço da Foto 3x4
        draw.rectangle([450, 120, 560, 270], outline=preto, width=2)
        draw.text((485, 190), "FOTO", fill=preto, font=fonte_padrao)

        # Salva a imagem temporariamente na pasta /tmp do Linux/Docker
        caminho_arquivo = f"/tmp/cartao_{cartao_id}.jpg"
        img.save(caminho_arquivo, quality=95)

        return caminho_arquivo

    def enviar_email_aprovacao(
        self, destinatario: str, nome_aluno: str, cartao_id: int
    ):
        """
        Gera a arte do cartão, anexa no e-mail HTML e faz o disparo.
        """
        if not self.remetente or not self.senha:
            return False

        assunto = "🎉 Bem-vindo(a) ao Cursinho ExpliCAASO! Seu cartão de acesso chegou."

        corpo_html = f"""
        <html>
            <body>
                <h2>Olá, {nome_aluno}!</h2>
                <p>É com muita alegria que anunciamos a sua aprovação no processo seletivo do <b>Cursinho ExpliCAASO</b>!</p>
                <p>Em anexo neste e-mail, você encontrará o seu <b>Cartão de Acesso Provisório</b>.</p>
                <p>O seu número de identificação para registrar presença é o <b>{cartao_id}</b>. Você pode baixar a imagem do cartão e salvá-la no seu celular.</p>
                <br>
                <p>Nos vemos na sala de aula!</p>
                <p>Um abraço,<br><b>Equipe ExpliCAASO</b></p>
            </body>
        </html>
        """

        msg = MIMEMultipart()
        msg["From"] = self.remetente
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo_html, "html"))

        # 1. Gera a imagem física do cartão
        caminho_imagem = self._gerar_imagem_cartao(nome_aluno, cartao_id)

        try:
            # 2. Lê a imagem e anexa no e-mail
            with open(caminho_imagem, "rb") as f:
                img_data = f.read()

            image_attachment = MIMEImage(
                img_data, name=f"Cartao_ExpliCAASO_{cartao_id}.jpg"
            )
            msg.attach(image_attachment)

            # 3. Dispara pelo Gmail
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
                servidor.login(self.remetente, self.senha)
                servidor.send_message(msg)

            return True

        except Exception as e:
            print(f"❌ Erro ao enviar e-mail para {destinatario}: {e}")
            return False

        finally:
            # 4. Limpa o terreno (Deleta a imagem gerada para não lotar o servidor do cursinho com o tempo)
            if os.path.exists(caminho_imagem):
                os.remove(caminho_imagem)
