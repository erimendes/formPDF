# /home/francisco/formPDF/projeto/geradores/salvar_texto_em_arquivo.py
import os

def salvar_texto_em_arquivo(texto, nome_arquivo, upload_folder):
    caminho_txt = os.path.join(upload_folder, nome_arquivo)
    with open(caminho_txt, 'w', encoding='utf-8') as f:
        f.write(texto)
    return caminho_txt