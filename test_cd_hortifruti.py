#!/usr/bin/env python3
"""
Script de teste para verificar o processamento da planilha CD HORTIFRUTI
"""

import pandas as pd
import os
import sys

def test_planilha_cd_hortifruti():
    """Testa o processamento da planilha CD HORTIFRUTI"""
    
    # Caminho para a planilha de exemplo
    planilha_path = 'exemplos_planilhas/PLANILHA BASE HORTI GERAL.xlsx'
    
    if not os.path.exists(planilha_path):
        print(f"Erro: Planilha não encontrada em {planilha_path}")
        return
    
    try:
        # Ler a planilha
        print("Lendo planilha...")
        df = pd.read_excel(planilha_path)
        
        print(f"Colunas da planilha: {df.columns.tolist()}")
        print(f"Total de linhas: {len(df)}")
        print("\nPrimeiras 5 linhas:")
        print(df.head())
        
        # Identificar colunas
        fornecedores = []
        lojas = []
        colunas_principais = []
        
        # Normalizar todas as colunas removendo espaços extras
        df.columns = [str(col).strip() for col in df.columns]
        
        for col in df.columns:
            print(f"Analisando coluna: '{col}'")
            
            # Verificar se é fornecedor (começa com #)
            if col.startswith('#'):
                fornecedores.append(col)
                print(f"  -> Fornecedor identificado: {col}")
            # Verificar se é loja (começa com *)
            elif col.startswith('*'):
                lojas.append(col)
                print(f"  -> Loja identificada: {col}")
            # Verificar se é loja sem prefixo * (contém nomes específicos)
            elif any(loja_nome in col.upper() for loja_nome in ['PITUBA', 'VILAS', 'VITORIA', 'APIPEMA', 'RESTAURANTE', 'PADARIA']):
                lojas.append(col)
                print(f"  -> Loja sem prefixo identificada: {col}")
            else:
                colunas_principais.append(col)
                print(f"  -> Coluna principal: {col}")
        
        print(f"\nFornecedores encontrados: {fornecedores}")
        print(f"Lojas encontradas: {lojas}")
        print(f"Colunas principais: {colunas_principais}")
        
        # Testar processamento de um fornecedor específico
        if fornecedores:
            fornecedor_teste = fornecedores[0]
            print(f"\nTestando fornecedor: {fornecedor_teste}")
            
            produtos_fornecedor = []
            for i, produto in enumerate(df.to_dict('records')):
                valor_fornecedor = produto.get(fornecedor_teste)
                
                if (valor_fornecedor is not None and 
                    pd.notna(valor_fornecedor) and 
                    float(valor_fornecedor) > 0):
                    
                    # Obter código do produto
                    codigo_produto = produto.get('COD.', '')
                    if pd.notna(codigo_produto):
                        codigo_produto = str(int(float(codigo_produto)))
                    else:
                        codigo_produto = ''
                    
                    # Obter nome do produto
                    nome_produto = produto.get('NOME DO PRODUTO', '')
                    if pd.notna(nome_produto):
                        nome_produto = str(nome_produto).strip()
                    else:
                        nome_produto = codigo_produto
                    
                    # Obter unidade
                    unidade_produto = produto.get('Und.', '')
                    if pd.notna(unidade_produto):
                        unidade_produto = str(unidade_produto).strip()
                    else:
                        unidade_produto = ''
                    
                    produto_info = {
                        'codigo': codigo_produto,
                        'nome': nome_produto,
                        'unidade': unidade_produto,
                        'quantidade_fornecedor': float(valor_fornecedor),
                        'lojas': {}
                    }
                    
                    # Adicionar quantidades das lojas
                    for loja in lojas:
                        valor_loja = produto.get(loja, 0)
                        if valor_loja is not None and pd.notna(valor_loja) and str(valor_loja).strip() != '':
                            produto_info['lojas'][loja] = float(valor_loja)
                        else:
                            produto_info['lojas'][loja] = 0.0
                    
                    produtos_fornecedor.append(produto_info)
                    print(f"  Produto {i}: {produto_info['codigo']} - {produto_info['nome']} - Qtd: {produto_info['quantidade_fornecedor']}")
            
            print(f"\nTotal de produtos para {fornecedor_teste}: {len(produtos_fornecedor)}")
            
            # Mostrar alguns produtos como exemplo
            if produtos_fornecedor:
                print("\nExemplos de produtos:")
                for i, produto in enumerate(produtos_fornecedor[:3]):
                    print(f"  {i+1}. Código: {produto['codigo']}")
                    print(f"     Nome: {produto['nome']}")
                    print(f"     Unidade: {produto['unidade']}")
                    print(f"     Qtd Fornecedor: {produto['quantidade_fornecedor']}")
                    print(f"     Lojas: {produto['lojas']}")
                    print()
        
        print("\nTeste concluído com sucesso!")
        
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_planilha_cd_hortifruti() 