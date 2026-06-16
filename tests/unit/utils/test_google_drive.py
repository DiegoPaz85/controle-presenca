import pytest
import os
from unittest.mock import patch, MagicMock
from src.controle_presenca.utils.google_drive import GoogleDriveDownloader
from src.controle_presenca.config.settings import settings

class TestGoogleDriveDownloader:
    @patch('os.path.exists')
    def test_obter_servico_falta_credentials(self, mock_exists):
        """Testa que erro é lançado se o credentials.json não existir"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError) as exc_info:
            GoogleDriveDownloader.obter_servico()
            
        assert "credentials.json não encontrado" in str(exc_info.value)

    @patch('os.path.exists')
    @patch('src.controle_presenca.utils.google_drive.service_account.Credentials.from_service_account_file')
    @patch('src.controle_presenca.utils.google_drive.build')
    def test_obter_servico_sucesso(self, mock_build, mock_from_file, mock_exists):
        """Testa inicialização do serviço com credenciais existentes"""
        mock_exists.return_value = True
        mock_from_file.return_value = MagicMock()
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GoogleDriveDownloader.obter_servico()
        
        assert service == mock_service
        mock_build.assert_called_once_with('drive', 'v3', credentials=mock_from_file.return_value)

    @patch('src.controle_presenca.utils.google_drive.GoogleDriveDownloader.obter_servico')
    @patch('builtins.open')
    @patch('src.controle_presenca.utils.google_drive.MediaIoBaseDownload')
    def test_baixar_planilha_forms_sucesso(self, mock_downloader_class, mock_open, mock_obter_servico):
        """Testa download com sucesso do formulário do Drive"""
        mock_service = MagicMock()
        mock_obter_servico.return_value = mock_service
        
        # Simula resposta da listagem de arquivos
        mock_service.files().list().execute.return_value = {
            'files': [{'id': '123456'}]
        }
        
        # Simula downloader finalizado
        mock_downloader = MagicMock()
        mock_downloader.next_chunk.return_value = (None, True)
        mock_downloader_class.return_value = mock_downloader
        
        res = GoogleDriveDownloader.baixar_planilha_forms("caminho_saida.xlsx")
        
        assert res is True
        mock_service.files().export_media.assert_called_once_with(
            fileId='123456',
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        mock_downloader.next_chunk.assert_called_once()

    @patch('src.controle_presenca.utils.google_drive.GoogleDriveDownloader.obter_servico')
    def test_baixar_planilha_forms_erro_nao_encontrado(self, mock_obter_servico):
        """Testa erro lançado se o arquivo não for encontrado no Drive"""
        mock_service = MagicMock()
        mock_obter_servico.return_value = mock_service
        
        # Listagem vazia
        mock_service.files().list().execute.return_value = {
            'files': []
        }
        
        with pytest.raises(FileNotFoundError) as exc_info:
            GoogleDriveDownloader.baixar_planilha_forms("saida.xlsx")
            
        assert "não encontrado no Google Drive" in str(exc_info.value)
