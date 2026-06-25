import os
import logging

logger = logging.getLogger(__name__)

def gerar_imagem_cartao(cartao_id: int, nome_aluno: str, output_dir: str) -> str:
    """
    Gera uma imagem JPG do cartão de presença para o aluno.
    Usa Pillow se disponível para desenhar o cartão, ou cria um arquivo placeholder 
    para garantir compatibilidade em ambientes sem dependências C/Rust.
    """
    os.makedirs(output_dir, exist_ok=True)
    caminho_imagem = os.path.join(output_dir, f"{cartao_id}.jpg")

    try:
        from PIL import Image, ImageDraw, ImageFont
        # Cria imagem com fundo branco (400x250 pixels)
        img = Image.new('RGB', (400, 250), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Desenha uma borda azul
        draw.rectangle([(10, 10), (390, 240)], outline=(33, 150, 243), width=5)
        
        # Cabeçalho do ExpliCAASO
        draw.text((30, 30), "ExpliCAASO Cursinho Popular", fill=(33, 150, 243))
        draw.text((30, 60), "CARTÃO DE PRESENÇA", fill=(0, 0, 0))
        
        # Nome do Aluno e Cartão
        draw.text((30, 110), f"Aluno: {nome_aluno.upper()}", fill=(0, 0, 0))
        draw.text((30, 150), f"ID Cartão: {cartao_id}", fill=(0, 0, 0))
        draw.text((30, 190), "Apresente o QR Code no leitor", fill=(100, 100, 100))
        
        img.save(caminho_imagem, "JPEG")
        logger.info(f"Imagem do cartão gerada com Pillow para {nome_aluno}: {caminho_imagem}")
        
    except ImportError:
        # Fallback se Pillow não estiver instalado
        # Cria um arquivo texto/mock com os dados ou escreve um arquivo mínimo
        with open(caminho_imagem, "wb") as f:
            # Escreve um cabeçalho fictício de JPG ou apenas dados de identificação em bytes
            # Para testes e fallback, escrever o texto do cartão em bytes é suficiente
            f.write(f"CARTAO ID: {cartao_id}\nALUNO: {nome_aluno}\nSTATUS: ATIVADO".encode('utf-8'))
        logger.warning(f"Pillow não disponível. Criado placeholder para o cartão {cartao_id} em {caminho_imagem}")

    return caminho_imagem
