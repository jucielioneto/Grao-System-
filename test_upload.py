#!/usr/bin/env python3
"""
Script para testar o upload da planilha CD HORTIFRUTI
"""

import requests
import os
import sys

def test_upload():
    """Testa o upload da planilha"""
    
    # URL do sistema (local ou Railway)
    base_url = "http://localhost:5000"  # Mude para a URL do Railway se necessário
    
    # Caminho para a planilha de exemplo
    planilha_path = 'exemplos_planilhas/PLANILHA BASE HORTI GERAL.xlsx'
    
    if not os.path.exists(planilha_path):
        print(f"Erro: Planilha não encontrada em {planilha_path}")
        return
    
    try:
        # Preparar o arquivo para upload
        with open(planilha_path, 'rb') as f:
            files = {'planilha': (os.path.basename(planilha_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"Enviando arquivo para {base_url}/cd_hortifruti_upload...")
            
            # Fazer o upload
            response = requests.post(f"{base_url}/cd_hortifruti_upload", files=files)
            
            print(f"Status da resposta: {response.status_code}")
            print(f"Conteúdo da resposta: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Upload bem-sucedido!")
                print(f"Fornecedores encontrados: {data.get('fornecedores', [])}")
                print(f"Lojas encontradas: {data.get('lojas', [])}")
                print(f"Mensagem: {data.get('message', '')}")
            else:
                print(f"Erro no upload: {response.status_code}")
                print(f"Resposta: {response.text}")
                
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload() 