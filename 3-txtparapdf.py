from flask import Flask, request, send_file, render_template_string
import qrcode
from fpdf import FPDF
import os
import shutil
import unicodedata

app = Flask(__name__)

# Remove acentos e caracteres especiais
def remover_caracteres_especiais(texto):
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

# Divide o txt em blocos de questões
def processar_txt(conteudo):
    blocos = conteudo.strip().split("\n\n")
    questoes = []

    for bloco in blocos:
        linhas = bloco.strip().split("\n")
        if len(linhas) < 2:
            continue
        link = linhas[0].strip()
        texto = "\n".join(linhas[1:]).strip()
        questoes.append({"link": link, "texto": texto})
    
    return questoes

# Gera o PDF com todas as questões + QR codes
def gerar_pdf_com_qrcodes(questoes, nome_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    temp_dir = "qrcodes_temp"
    os.makedirs(temp_dir, exist_ok=True)

    for idx, questao in enumerate(questoes, start=1):
        pdf.add_page()

        # Gerar QR code
        qr_path = os.path.join(temp_dir, f"qrcode_{idx}.png")
        qr = qrcode.make(questao["link"])
        qr.save(qr_path)

        # Inserir QR code
        pdf.image(qr_path, x=10, y=10, w=30)

        # Link ao lado do QR code
        pdf.set_xy(45, 15)
        link_limpo = remover_caracteres_especiais(questao["link"])
        pdf.multi_cell(0, 10, f"{link_limpo}")

        # Pular para a linha abaixo do QR code (altura do QR = 30)
        pdf.set_y(50)

        # Adicionar texto da questão indentado
        texto_formatado = "\n".join("       " + linha for linha in questao["texto"].splitlines())
        texto_limpo = remover_caracteres_especiais(texto_formatado)
        pdf.multi_cell(0, 8, texto_limpo)

    pdf.output(nome_pdf)
    shutil.rmtree(temp_dir)

@app.route('/')
def home():
    return render_template_string(open('index.html', encoding='utf-8').read())

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    if 'arquivo' not in request.files:
        return 'Arquivo não enviado.', 400

    arquivo = request.files['arquivo']
    if not arquivo.filename.endswith('.txt'):
        return 'Apenas arquivos .txt são permitidos.', 400

    conteudo = arquivo.read().decode('utf-8')
    questoes = processar_txt(conteudo)
    
    if not questoes:
        return 'Nenhuma questão válida encontrada.', 400

    output_pdf = 'questoes_com_qrcode.pdf'
    gerar_pdf_com_qrcodes(questoes, output_pdf)

    return send_file(output_pdf, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
