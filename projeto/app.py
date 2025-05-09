from flask import Flask, request, send_file, render_template_string, jsonify
from fpdf import FPDF
import unicodedata
import os

# Importe a função de processamento de questões
from processamento import processar_txt

# Importe as funções de geração
from geradores.gerar_pdf_com_layout import gerar_pdf_com_layout
from geradores.gerar_pdf_com_resposta import gerar_pdf_com_resposta
from geradores.gerar_json import gerar_json
from geradores.gerar_txt import gerar_txt

from geradores.converter_pdf_para_txt import converter_pdf_para_txt
from geradores.salvar_texto_em_arquivo import salvar_texto_em_arquivo

# Importe a função de filtragem do local correto
from geradores.filtrar_questoes_conteudo import filtrar_questoes_conteudo

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'  # Você pode escolher outro nome para a pasta
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Opcional, mas pode ser útil para configurações futuras

def remover_caracteres_especiais(texto):
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

@app.route('/')
def home():
    return render_template_string(open('templates/index.html', encoding='utf-8').read())

@app.route('/filtrar', methods=['POST'])
def filtrar():
    if 'arquivo' not in request.files:
        return 'Arquivo não enviado.', 400
    arquivo = request.files['arquivo']
    if not arquivo.filename.endswith('.txt'):
        return 'Apenas arquivos .txt são permitidos.', 400
    conteudo = arquivo.read().decode('utf-8')
    questoes_filtradas = filtrar_questoes_conteudo(conteudo)  # A função agora está importada diretamente
    output_path = 'questoes_filtradas.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(questoes_filtradas)
    return send_file(output_path, as_attachment=True)

@app.route('/gerar_arquivos', methods=['POST'])
def gerar_arquivos():
    if 'arquivo' not in request.files:
        return 'Arquivo não enviado.', 400
    arquivo = request.files['arquivo']
    if not arquivo.filename.endswith('.txt'):
        return 'Apenas arquivos .txt são permitidos.', 400
    conteudo = arquivo.read().decode('utf-8')
    questoes = processar_txt(conteudo)
    if not questoes:
        return 'Nenhuma questão válida encontrada.', 400
    gerar_pdf_com_layout(questoes, 'questoes_com_layout.pdf')
    gerar_pdf_com_resposta(questoes, 'questoes_apenas_respostas.pdf')
    gerar_json(questoes, 'questoes.json')
    gerar_txt(questoes, 'questoes.txt')
    return send_file('questoes_apenas_respostas.pdf', as_attachment=True, download_name='questoes_apenas_respostas.pdf')

@app.route('/converter', methods=['POST'])
def converter():
    # Verifica se o arquivo foi enviado
    if 'pdf' not in request.files:
        return jsonify({"error": "Nenhum arquivo PDF enviado"}), 400
    
    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    # Salva o arquivo temporariamente
    caminho_pdf = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(caminho_pdf)

    # Converte o PDF para texto
    texto_convertido = converter_pdf_para_txt(caminho_pdf)

    # Salva o texto extraído em um arquivo .txt
    nome_arquivo_txt = pdf_file.filename.rsplit('.', 1)[0] + '.txt'
    caminho_txt = salvar_texto_em_arquivo(texto_convertido, nome_arquivo_txt, UPLOAD_FOLDER)  # Passe UPLOAD_FOLDER

    # Retorna o caminho do arquivo .txt gerado
    return jsonify({"texto": texto_convertido, "caminho_txt": caminho_txt})

if __name__ == '__main__':
    app.run(debug=True, port=5001)