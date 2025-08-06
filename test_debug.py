#!/usr/bin/env python3
import pandas as pd
import json

def test_fornecedor_processing():
    # Caminho para a planilha exemplo
    planilha_path = 'exemplos_planilhas/PLANILHA BASE HORTI GERAL.xlsx'
    
    try:
        # Ler a planilha
        df = pd.read_excel(planilha_path)
        print("=== PLANILHA LIDA COM SUCESSO ===")
        
        # Normalizar colunas
        df.columns = [str(col).strip() for col in df.columns]
        
        # Identificar fornecedores e lojas
        fornecedores = [col for col in df.columns if col.startswith('#')]
        lojas = [col for col in df.columns if col.startswith('*')]
        
        print(f"Fornecedores: {fornecedores}")
        print(f"Lojas: {lojas}")
        
        # Simular o processamento do fornecedor #ERICO
        fornecedor = '#ERICO'
        dados = df.to_dict('records')
        
        print(f"\n=== PROCESSANDO FORNECEDOR: {fornecedor} ===")
        
        produtos_fornecedor = []
        for i, produto in enumerate(dados):
            try:
                print(f"\n--- Produto {i} ---")
                print(f"Dados do produto: {produto}")
                
                # Verificar se o fornecedor existe e tem quantidade > 0
                valor_fornecedor = produto.get(fornecedor)
                print(f"Valor do fornecedor: {valor_fornecedor} - Tipo: {type(valor_fornecedor)}")
                
                if (fornecedor in produto and 
                    valor_fornecedor is not None and 
                    pd.notna(valor_fornecedor) and 
                    float(valor_fornecedor) > 0):
                    
                    print(f"✓ Produto {i} tem quantidade > 0 para fornecedor {fornecedor}")
                    
                    produto_info = {
                        'codigo': str(produto.get('COD.', '')).strip(),
                        'nome': str(produto.get('NOME DO PRODUTO', '')).strip(),
                        'unidade': str(produto.get('Und.', '')).strip(),
                        'quantidade_fornecedor': float(valor_fornecedor),
                        'lojas': {}
                    }
                    
                    print(f"Informações do produto: {produto_info}")
                    
                    # Adicionar quantidades das lojas
                    for loja in lojas:
                        valor_loja = produto.get(loja, 0)
                        print(f"Loja '{loja}' - Valor: {valor_loja} - Tipo: {type(valor_loja)}")
                        
                        if valor_loja is not None and pd.notna(valor_loja) and str(valor_loja).strip() != '':
                            produto_info['lojas'][loja] = float(valor_loja)
                        else:
                            produto_info['lojas'][loja] = 0.0
                    
                    produtos_fornecedor.append(produto_info)
                    print(f"✓ Produto {i} adicionado - Código: {produto_info['codigo']}, Qtd: {produto_info['quantidade_fornecedor']}")
                    print(f"Lojas do produto: {produto_info['lojas']}")
                else:
                    print(f"✗ Produto {i} não tem quantidade > 0 para fornecedor {fornecedor}")
                    
            except (ValueError, TypeError) as e:
                print(f"Erro ao processar produto {i}: {e}")
                continue
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de produtos filtrados: {len(produtos_fornecedor)}")
        
        # Testar JSON serialization
        response_data = {
            'fornecedor': fornecedor,
            'produtos': produtos_fornecedor,
            'lojas': lojas
        }
        
        try:
            json_str = json.dumps(response_data, indent=2)
            print("✓ JSON serialization OK")
            print(f"Tamanho do JSON: {len(json_str)} caracteres")
        except Exception as e:
            print(f"✗ Erro na serialização JSON: {e}")
        
        # Mostrar alguns produtos como exemplo
        print(f"\n=== EXEMPLOS DE PRODUTOS ===")
        for i, produto in enumerate(produtos_fornecedor[:3]):
            print(f"Produto {i}: {produto}")
        
    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fornecedor_processing() 