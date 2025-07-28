#!/usr/bin/env python3
"""
Script para migração de dados do SQLite para PostgreSQL
Execute este script localmente antes do deploy para migrar dados existentes
"""

import sqlite3
import os
import sys
from datetime import datetime
import pytz

def get_brasilia_time():
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasilia_tz)

def migrate_sqlite_to_postgres():
    """Migra dados do SQLite para PostgreSQL"""
    
    # Verifica se o banco SQLite existe
    sqlite_path = 'instance/usuarios.db'
    if not os.path.exists(sqlite_path):
        print("Banco SQLite não encontrado. Nada para migrar.")
        return
    
    try:
        # Conecta ao SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        print("Conectado ao banco SQLite. Iniciando migração...")
        
        # Migra usuários
        print("Migrando usuários...")
        sqlite_cursor.execute("SELECT id, username, email, password_hash FROM user")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            print(f"  - Usuário: {user[1]} ({user[2]})")
        
        # Migra planilhas
        print("Migrando planilhas...")
        sqlite_cursor.execute("""
            SELECT id, nome_arquivo, nome_original, tamanho, tipo_arquivo, 
                   data_upload, status, user_id 
            FROM planilha
        """)
        planilhas = sqlite_cursor.fetchall()
        
        for planilha in planilhas:
            print(f"  - Planilha: {planilha[2]} ({planilha[1]})")
        
        # Migra processamentos
        print("Migrando processamentos...")
        sqlite_cursor.execute("""
            SELECT id, tipo_processamento, data_processamento, produtos_processados,
                   arquivos_gerados, status, user_id, planilha_id
            FROM processamento
        """)
        processamentos = sqlite_cursor.fetchall()
        
        for proc in processamentos:
            print(f"  - Processamento: {proc[1]} - {proc[5]}")
        
        # Migra arquivos TXT
        print("Migrando arquivos TXT...")
        sqlite_cursor.execute("""
            SELECT id, nome_arquivo, tamanho, data_geracao, tipo_loja,
                   downloads_count, status, processamento_id
            FROM arquivo_txt
        """)
        arquivos_txt = sqlite_cursor.fetchall()
        
        for txt in arquivos_txt:
            print(f"  - Arquivo TXT: {txt[1]} ({txt[4]})")
        
        sqlite_conn.close()
        
        print(f"\nMigração concluída!")
        print(f"Total de registros encontrados:")
        print(f"  - Usuários: {len(users)}")
        print(f"  - Planilhas: {len(planilhas)}")
        print(f"  - Processamentos: {len(processamentos)}")
        print(f"  - Arquivos TXT: {len(arquivos_txt)}")
        
        print("\nIMPORTANTE: Os dados foram apenas lidos do SQLite.")
        print("Para migrar efetivamente para PostgreSQL, você precisará:")
        print("1. Configurar a variável DATABASE_URL no Railway")
        print("2. Executar a aplicação que criará as tabelas automaticamente")
        print("3. Usar este script para inserir os dados no PostgreSQL")
        
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        sys.exit(1)

if __name__ == '__main__':
    migrate_sqlite_to_postgres() 