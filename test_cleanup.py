#!/usr/bin/env python3
"""
Script para testar o sistema de limpeza de arquivos
Execute este script para verificar o funcionamento da limpeza
"""

import os
import sys
from app import app
from file_cleanup import cleanup_manager

def test_cleanup():
    """Testa o sistema de limpeza"""
    
    with app.app_context():
        print("=== Teste do Sistema de Limpeza ===\n")
        
        # 1. Mostra estatísticas atuais
        print("1. Estatísticas de Armazenamento:")
        stats = cleanup_manager.get_storage_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        
        print("\n2. Configurações de Limpeza:")
        print(f"   Máximo uso de disco: {cleanup_manager.max_disk_usage_percent}%")
        print(f"   Idade máxima dos arquivos: {cleanup_manager.max_file_age_days} dias")
        print(f"   Espaço livre mínimo: {cleanup_manager.min_free_space_mb} MB")
        
        # 3. Executa limpeza
        print("\n3. Executando limpeza...")
        removed_files, freed_space = cleanup_manager.perform_cleanup()
        
        print(f"   Arquivos removidos: {removed_files}")
        print(f"   Espaço liberado: {freed_space / (1024*1024):.2f} MB")
        
        # 4. Mostra estatísticas após limpeza
        print("\n4. Estatísticas após limpeza:")
        stats_after = cleanup_manager.get_storage_stats()
        for key, value in stats_after.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        
        print("\n=== Teste concluído ===")

if __name__ == '__main__':
    test_cleanup() 