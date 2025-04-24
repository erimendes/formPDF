# Biblioteca a ser instalada:
# pip install pdfminer.six

from pdfminer.high_level import extract_text
import csv

def pdf_para_csv(caminho_pdf, caminho_csv):
    """Extrai texto de um PDF e salva em um arquivo CSV."""

    try:
        texto = extract_text(caminho_pdf)
        linhas = texto.split('\n')  # Divide o texto em linhas

        with open(caminho_csv, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor_csv = csv.writer(arquivo_csv)
            for linha in linhas:
                colunas = linha.split(';') # Assume que os dados são separados por ponto e virgula. Caso deseje outro separador como virgula ou espaço mude essa linha.
                escritor_csv.writerow(colunas)

        print(f"Arquivo CSV criado com sucesso em: {caminho_csv}")

    except FileNotFoundError:
        print(f"Erro: Arquivo PDF não encontrado em: {caminho_pdf}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Exemplo de uso
caminho_pdf = 'caminho/para/seu/arquivo.pdf'
caminho_csv = 'caminho/para/seu/arquivo.csv'

pdf_para_csv(caminho_pdf, caminho_csv)