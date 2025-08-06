#!/usr/bin/env python3
"""
Teste para verificar a funcionalidade de filtragem de linhas zeradas
na planilha de Hortifruti
"""

import pandas as pd
import numpy as np

def test_filtragem_linhas_zeradas():
    """Testa a lógica de filtragem de linhas zeradas"""
    
    # Cria um DataFrame de teste com algumas linhas zeradas
    data = {
        'Cod.': [1001, 1002, 1003, 1004, 1005, 1006],
        'Nome do Produto': ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E', 'Produto F'],
        'Pedido Pituba': [10, 0, 5, 0, 0, 15],
        'Pedido Vitoria': [0, 20, 0, 0, 0, 8],
        'Pedido Vilas': [5, 0, 0, 0, 0, 12],
        'Pedido Apipema': [0, 0, 0, 0, 0, 3]
    }
    
    df = pd.DataFrame(data)
    print("DataFrame original:")
    print(df)
    print(f"Total de linhas: {len(df)}")
    print()
    
    # Aplica a lógica de filtragem (mesma do código principal)
    lojas = {
        'Pedido Pituba': 'pituba',
        'Pedido Vitoria': 'vitoria',
        'Pedido Vilas': 'vilas',
        'Pedido Apipema': 'apipema'
    }
    
    # Cria uma máscara para identificar linhas com pelo menos uma quantidade > 0
    colunas_quantidade = list(lojas.keys())
    df['tem_quantidade'] = False
    
    for idx, row in df.iterrows():
        tem_quantidade = False
        for col in colunas_quantidade:
            if col in df.columns:
                quantidade = row.get(col, 0)
                if pd.notna(quantidade) and float(quantidade) > 0:
                    tem_quantidade = True
                    break
        df.at[idx, 'tem_quantidade'] = tem_quantidade
    
    # Filtra apenas linhas que têm pelo menos uma quantidade > 0
    df_filtrado = df[df['tem_quantidade'] == True].copy()
    linhas_removidas = len(df) - len(df_filtrado)
    
    # Remove a coluna auxiliar
    df_filtrado = df_filtrado.drop('tem_quantidade', axis=1)
    
    print("DataFrame após filtragem:")
    print(df_filtrado)
    print(f"Linhas após filtragem: {len(df_filtrado)}")
    print(f"Linhas zeradas removidas: {linhas_removidas}")
    print()
    
    # Verifica se a filtragem está correta
    linhas_esperadas = 3  # Produtos A, B, C e F têm pelo menos uma quantidade > 0
    linhas_zeradas_esperadas = 2  # Produtos D e E têm todas as quantidades = 0
    
    print("Verificação:")
    print(f"Linhas esperadas após filtragem: {linhas_esperadas}")
    print(f"Linhas zeradas esperadas removidas: {linhas_zeradas_esperadas}")
    print(f"Teste passou: {len(df_filtrado) == linhas_esperadas and linhas_removidas == linhas_zeradas_esperadas}")
    
    return len(df_filtrado) == linhas_esperadas and linhas_removidas == linhas_zeradas_esperadas

if __name__ == "__main__":
    print("=== Teste de Filtragem de Linhas Zeradas ===")
    print()
    
    sucesso = test_filtragem_linhas_zeradas()
    
    print()
    print("=" * 50)
    if sucesso:
        print("✅ Teste PASSOU - Filtragem funcionando corretamente!")
    else:
        print("❌ Teste FALHOU - Verificar lógica de filtragem")
    print("=" * 50) 