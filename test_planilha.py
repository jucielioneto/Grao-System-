#!/usr/bin/env python3
import pandas as pd
import os

def test_planilha():
    # Caminho para a planilha exemplo
    planilha_path = 'exemplos_planilhas/PLANILHA BASE HORTI GERAL.xlsx'
    
    if not os.path.exists(planilha_path):
        print(f"Erro: Arquivo {planilha_path} não encontrado!")
        return
    
    try:
        # Ler a planilha
        df = pd.read_excel(planilha_path)
        print("=== PLANILHA LIDA COM SUCESSO ===")
        print(f"Colunas: {df.columns.tolist()}")
        print(f"Total de linhas: {len(df)}")
        
        # Normalizar colunas
        df.columns = [str(col).strip() for col in df.columns]
        print(f"\nColunas normalizadas: {df.columns.tolist()}")
        
        # Identificar fornecedores e lojas
        fornecedores = [col for col in df.columns if col.startswith('#')]
        lojas = [col for col in df.columns if col.startswith('*')]
        
        print(f"\nFornecedores encontrados: {fornecedores}")
        print(f"Lojas encontradas: {lojas}")
        
        # Verificar dados do primeiro produto
        if len(df) > 0:
            primeiro_produto = df.iloc[0]
            print(f"\n=== PRIMEIRO PRODUTO ===")
            print(f"Código: {primeiro_produto.get('COD.', 'N/A')}")
            print(f"Nome: {primeiro_produto.get('NOME DO PRODUTO', 'N/A')}")
            print(f"Unidade: {primeiro_produto.get('Und.', 'N/A')}")
            
            print(f"\nQuantidades dos fornecedores:")
            for fornecedor in fornecedores:
                valor = primeiro_produto.get(fornecedor, 0)
                print(f"  {fornecedor}: {valor}")
            
            print(f"\nQuantidades das lojas:")
            for loja in lojas:
                valor = primeiro_produto.get(loja, 0)
                print(f"  {loja}: {valor}")
        
        # Verificar se há valores NaN
        print(f"\n=== VERIFICAÇÃO DE VALORES NaN ===")
        for col in df.columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                print(f"Coluna {col}: {nan_count} valores NaN")
        
    except Exception as e:
        print(f"Erro ao ler planilha: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_planilha() 