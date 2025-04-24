# Instale as bibliotecas:
# pip install tabula-py pandas

import tabula
import pandas as pd

def pdf_tabela_para_csv(caminho_pdf, caminho_csv):
    """Extrai tabelas de um PDF e salva em um arquivo CSV."""
    try:
        tabelas = tabula.read_pdf(caminho_pdf, pages='all', multiple_tables=True)

        if tabelas:
            # Concatena todas as tabelas em um único DataFrame
            dataframe_concatenado = pd.concat(tabelas, ignore_index=True)

            dataframe_concatenado.to_csv(caminho_csv, index=False)
            print(f"Arquivo CSV criado com sucesso em: {caminho_csv}")

        else:
            print("Nenhuma tabela encontrada no arquivo PDF.")
    except FileNotFoundError:
        print(f"Erro: Arquivo PDF não encontrado em: {caminho_pdf}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Exemplo de uso
caminho_pdf = 'caminho/para/seu/arquivo.pdf'
caminho_csv = 'caminho/para/seu/arquivo.csv'

pdf_tabela_para_csv(caminho_pdf, caminho_csv)