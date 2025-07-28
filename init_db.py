#!/usr/bin/env python3
"""
Script para inicializar o banco de dados
Execute este script para criar as tabelas no PostgreSQL do Railway
"""

import os
import sys
from app import app, db, User, bcrypt
from datetime import datetime
import pytz

def get_brasilia_time():
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasilia_tz)

def init_database():
    """Inicializa o banco de dados criando as tabelas"""
    
    with app.app_context():
        try:
            print("Criando tabelas do banco de dados...")
            db.create_all()
            print("✓ Tabelas criadas com sucesso!")
            
            # Verifica se já existe um usuário admin
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("Criando usuário administrador...")
                password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
                
                admin_user = User(
                    username='admin',
                    email='admin@graosystem.com',
                    password_hash=password_hash
                )
                
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Usuário administrador criado!")
                print("  Usuário: admin")
                print("  Senha: admin123")
                print("  IMPORTANTE: Altere a senha após o primeiro login!")
            else:
                print("✓ Usuário administrador já existe")
            
            print("\nBanco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            sys.exit(1)

if __name__ == '__main__':
    init_database() 