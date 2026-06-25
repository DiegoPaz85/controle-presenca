import os
import io
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from ..config.settings import settings

logger = logging.getLogger(__name__)

class GoogleDriveDownloader:
    @staticmethod
    def obter_servico():
        caminho_credenciais = settings.GOOGLE_CREDENTIALS_PATH
        if not os.path.exists(caminho_credenciais):
            msg = (
                f"❌ Arquivo credentials.json não encontrado em: {caminho_credenciais}. "
                "Por favor, configure as credenciais do Google Drive neste caminho ou "
                "defina a variável de ambiente GOOGLE_CREDENTIALS_PATH no seu arquivo .env."
            )
            logger.error(msg)
            raise FileNotFoundError(msg)

        SCOPES = ['https://www.googleapis.com/auth/drive']
        try:
            credentials = service_account.Credentials.from_service_account_file(
                caminho_credenciais, scopes=SCOPES
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Erro ao autenticar com a API do Google Drive: {e}")
            raise RuntimeError(f"Erro de autenticação do Google Drive: {e}")

    @classmethod
    def baixar_planilha_forms(cls, output_path: str) -> bool:
        """
        Baixa o formulário de respostas do Google Drive e salva localmente como XLSX.
        """
        service = cls.obter_servico()
        folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
        file_name = settings.GOOGLE_DRIVE_FILE_NAME

        query = f"name='{file_name}' and '{folder_id}' in parents"
        try:
            response = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            files = response.get('files', [])

            if not files:
                # Caso não encontre com o folder_id, tenta buscar apenas pelo nome (mais tolerante)
                query_fallback = f"name='{file_name}'"
                response = service.files().list(q=query_fallback, spaces='drive', fields='files(id)').execute()
                files = response.get('files', [])

            if not files:
                msg = f"❌ Arquivo '{file_name}' não encontrado no Google Drive."
                logger.error(msg)
                raise FileNotFoundError(msg)

            file_id = files[0]['id']
            
            # Exporta como planilha Excel (XLSX)
            request = service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            with open(output_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            logger.info(f"✅ Download da planilha '{file_name}' concluído com sucesso em: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Erro durante o download do arquivo do Google Drive: {e}")
            raise e
