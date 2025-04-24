from flask import Flask, render_template, request, jsonify
import fitz  # PyMuPDF
import os

app = Flask(__name__)

# Cria o diretório 'uploads' se ele não existir
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def converter_pdf_para_txt(caminho_pdf):
    """Converte um arquivo PDF para texto usando PyMuPDF."""
    try:
        # Abre o arquivo PDF
        doc = fitz.open(caminho_pdf)
        texto = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            texto += page.get_text("text")
        return texto
    except Exception as e:
        return f"Erro durante a conversão: {e}"

def salvar_texto_em_arquivo(texto, nome_arquivo):
    """Salva o texto extraído em um arquivo .txt no diretório 'uploads'."""
    caminho_txt = os.path.join(UPLOAD_FOLDER, nome_arquivo)
    with open(caminho_txt, 'w', encoding='utf-8') as f:
        f.write(texto)
    return caminho_txt

@app.route('/')
def index():
    return render_template('index.html')

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
    nome_arquivo_txt = pdf_file.filename.rsplit('.', 1)[0] + '.txt'  # Renomeia o arquivo para .txt
    caminho_txt = salvar_texto_em_arquivo(texto_convertido, nome_arquivo_txt)

    # Retorna o caminho do arquivo .txt gerado
    return jsonify({"texto": texto_convertido, "caminho_txt": caminho_txt})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
