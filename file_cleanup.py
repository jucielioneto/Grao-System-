#!/usr/bin/env python3
"""
Sistema de limpeza automática de arquivos antigos
Gerencia o espaço em disco removendo arquivos antigos quando necessário
"""

import os
import shutil
from datetime import datetime, timedelta
from flask import current_app
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileCleanupManager:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        # Configurações de limpeza
        self.max_disk_usage_percent = int(app.config.get('MAX_DISK_USAGE_PERCENT', 80))
        self.max_file_age_days = int(app.config.get('MAX_FILE_AGE_DAYS', 30))
        self.min_free_space_mb = int(app.config.get('MIN_FREE_SPACE_MB', 100))
    
    def get_disk_usage(self, path):
        """Calcula o uso de disco em porcentagem"""
        try:
            total, used, free = shutil.disk_usage(path)
            usage_percent = (used / total) * 100
            free_mb = free / (1024 * 1024)
            return usage_percent, free_mb
        except Exception as e:
            logger.error(f"Erro ao calcular uso de disco: {e}")
            return 0, 0
    
    def get_file_age_days(self, file_path):
        """Calcula a idade do arquivo em dias"""
        try:
            if os.path.exists(file_path):
                file_time = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(file_time)
                age = datetime.now() - file_date
                return age.days
            return 0
        except Exception as e:
            logger.error(f"Erro ao calcular idade do arquivo {file_path}: {e}")
            return 0
    
    def cleanup_old_files(self, folder_path, max_age_days=None):
        """Remove arquivos antigos de uma pasta"""
        if max_age_days is None:
            max_age_days = self.max_file_age_days
        
        removed_count = 0
        removed_size = 0
        
        try:
            if not os.path.exists(folder_path):
                return removed_count, removed_size
            
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                
                if os.path.isfile(file_path):
                    age_days = self.get_file_age_days(file_path)
                    
                    if age_days > max_age_days:
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            removed_count += 1
                            removed_size += file_size
                            logger.info(f"Arquivo removido: {filename} (idade: {age_days} dias)")
                        except Exception as e:
                            logger.error(f"Erro ao remover arquivo {filename}: {e}")
        
        except Exception as e:
            logger.error(f"Erro ao limpar pasta {folder_path}: {e}")
        
        return removed_count, removed_size
    
    def cleanup_database_records(self, folder_type, db, Planilha, ArquivoTXT):
        """Remove registros do banco de dados para arquivos que não existem mais"""
        try:
            if folder_type == 'uploads':
                # Remove registros de planilhas que não existem mais
                planilhas = Planilha.query.filter_by(status='ativo').all()
                removed_count = 0
                
                for planilha in planilhas:
                    file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], planilha.nome_arquivo)
                    if not os.path.exists(file_path):
                        planilha.status = 'deletado'
                        removed_count += 1
                
                if removed_count > 0:
                    db.session.commit()
                    logger.info(f"Removidos {removed_count} registros de planilhas inexistentes")
            
            elif folder_type == 'txts':
                # Remove registros de arquivos TXT que não existem mais
                arquivos_txt = ArquivoTXT.query.filter_by(status='ativo').all()
                removed_count = 0
                
                for arquivo in arquivos_txt:
                    file_path = os.path.join(self.app.config['OUTPUT_FOLDER'], arquivo.nome_arquivo)
                    if not os.path.exists(file_path):
                        arquivo.status = 'deletado'
                        removed_count += 1
                
                if removed_count > 0:
                    db.session.commit()
                    logger.info(f"Removidos {removed_count} registros de arquivos TXT inexistentes")
        
        except Exception as e:
            logger.error(f"Erro ao limpar registros do banco: {e}")
    
    def perform_cleanup(self, db=None, Planilha=None, ArquivoTXT=None):
        """Executa a limpeza completa do sistema"""
        logger.info("Iniciando limpeza automática de arquivos...")
        
        total_removed_files = 0
        total_freed_space = 0
        
        # Verifica uso de disco
        uploads_path = self.app.config['UPLOAD_FOLDER']
        txts_path = self.app.config['OUTPUT_FOLDER']
        
        usage_percent, free_mb = self.get_disk_usage(uploads_path)
        
        logger.info(f"Uso de disco: {usage_percent:.1f}% | Espaço livre: {free_mb:.1f} MB")
        
        # Se o uso está alto ou espaço livre é baixo, executa limpeza
        if usage_percent > self.max_disk_usage_percent or free_mb < self.min_free_space_mb:
            logger.info("Limpeza necessária - iniciando remoção de arquivos antigos...")
            
            # Limpa arquivos antigos
            removed_uploads, freed_uploads = self.cleanup_old_files(uploads_path)
            removed_txts, freed_txts = self.cleanup_old_files(txts_path)
            
            total_removed_files = removed_uploads + removed_txts
            total_freed_space = freed_uploads + freed_txts
            
            # Limpa registros do banco se disponível
            if db and Planilha and ArquivoTXT:
                self.cleanup_database_records('uploads', db, Planilha, ArquivoTXT)
                self.cleanup_database_records('txts', db, Planilha, ArquivoTXT)
            
            logger.info(f"Limpeza concluída: {total_removed_files} arquivos removidos, {total_freed_space / (1024*1024):.2f} MB liberados")
        else:
            logger.info("Uso de disco dentro dos limites - limpeza não necessária")
        
        return total_removed_files, total_freed_space
    
    def get_storage_stats(self):
        """Retorna estatísticas de armazenamento"""
        try:
            uploads_path = self.app.config['UPLOAD_FOLDER']
            txts_path = self.app.config['OUTPUT_FOLDER']
            
            # Estatísticas de uploads
            uploads_size = 0
            uploads_count = 0
            if os.path.exists(uploads_path):
                for filename in os.listdir(uploads_path):
                    file_path = os.path.join(uploads_path, filename)
                    if os.path.isfile(file_path):
                        uploads_size += os.path.getsize(file_path)
                        uploads_count += 1
            
            # Estatísticas de TXTs
            txts_size = 0
            txts_count = 0
            if os.path.exists(txts_path):
                for filename in os.listdir(txts_path):
                    file_path = os.path.join(txts_path, filename)
                    if os.path.isfile(file_path):
                        txts_size += os.path.getsize(file_path)
                        txts_count += 1
            
            # Uso total de disco
            usage_percent, free_mb = self.get_disk_usage(uploads_path)
            
            return {
                'uploads_count': uploads_count,
                'uploads_size_mb': uploads_size / (1024 * 1024),
                'txts_count': txts_count,
                'txts_size_mb': txts_size / (1024 * 1024),
                'total_size_mb': (uploads_size + txts_size) / (1024 * 1024),
                'disk_usage_percent': usage_percent,
                'free_space_mb': free_mb,
                'max_disk_usage_percent': self.max_disk_usage_percent,
                'max_file_age_days': self.max_file_age_days
            }
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

# Instância global
cleanup_manager = FileCleanupManager() 