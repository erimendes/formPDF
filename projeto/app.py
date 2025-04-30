from flask import Flask, request, send_file, render_template_string
from fpdf import FPDF
import unicodedata

# Importe a função de processamento de questões do segundo arquivo
from processamento import processar_txt

# Importe as funções de geração do segundo arquivo
from geradores.gerar_pdf_com_layout import gerar_pdf_com_layout
from geradores.gerar_pdf_com_resposta import gerar_pdf_com_resposta
from geradores.gerar_json import gerar_json
from geradores.gerar_txt import gerar_txt

app = Flask(__name__)  # Descomente esta linha para inicializar a aplicação Flask

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
    # Assumindo que 'filtrar_questoes_conteudo' está definido em 'utils.py' e importado corretamente
    from utils import filtrar_questoes_conteudo
    questoes_filtradas = filtrar_questoes_conteudo(conteudo)
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)