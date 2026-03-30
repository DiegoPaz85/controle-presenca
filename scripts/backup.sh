#!/bin/bash

# Configurações
BACKUP_DIR="$(pwd)/backups"
DATA_ATUAL=$(date +"%Y%m%d_%H%M%S")
NOME_FICHEIRO="explicaaso_backup_$DATA_ATUAL.sql"

echo "🔄 Iniciando backup local..."
docker exec explicaaso_db pg_dump -U explicaaso_user -d explicaaso > "$BACKUP_DIR/$NOME_FICHEIRO"

if [[ $? -eq 0 ]]; then
    echo "✅ Backup local concluído: $NOME_FICHEIRO"
    
    echo "☁️ Enviando para o Google Drive..."
    # O rclone copia o arquivo para uma pasta chamada 'Backups_ExplicaASO' no seu Drive
    rclone copy "$BACKUP_DIR/$NOME_FICHEIRO" gdrive:Backups_ExplicaASO/
    
    if [[ $? -eq 0 ]]; then
        echo "🚀 Upload concluído com sucesso!"
    else
        echo "❌ Erro ao enviar para o Google Drive."
    fi
else
    echo "❌ Erro ao gerar o backup local."
fi
