from flask import Flask, render_template, request, send_file
import os
import csv
from pdfminer.high_level import extract_text
import uuid
import fitz  # PyMuPDF
from pyzbar import pyzbar
from PIL import Image
import io
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CSV_FOLDER = 'csv_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER

def corrigir_acentuacao(texto):
    """Corrige problemas comuns de acentuação no texto."""
    substituicoes = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã£": "ã",
        "Ã§": "ç",
        "Ãª": "ê",
        "Ã´": "ô",
        "Ã ": "à",
        "Ã¢": "â",
        "Ãµ": "õ",
        "Ã¼": "ü",
        "Ãª": "ê",
        "Ã´": "ô",
        "Ã ": "à",
        "Ã¢": "â",
        "Ãµ": "õ",
        "Ã¼": "ü",
        # Adicione mais substituições conforme necessário
    }
    for incorreto, correto in substituicoes.items():
        texto = texto.replace(incorreto, correto)
    return texto

def extrair_qr_codes(caminho_pdf):
    """Extrai e decodifica QR codes de um PDF."""
    qr_codes_encontrados = []
    try:
        pdf_document = fitz.open(caminho_pdf)
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            imagens = page.get_images(full=True)
            for img_index, img in enumerate(imagens):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                decoded_objects = pyzbar.decode(image)
                for obj in decoded_objects:
                    data = obj.data.decode("utf-8")
                    qr_codes_encontrados.append(data)
        return qr_codes_encontrados
    except Exception as e:
        return render_template('index.html', error=f"An error occurred: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return render_template('index.html', error="No file part")
        file = request.files['pdf_file']
        if file.filename == '':
            return render_template('index.html', error="No selected file")
        if file and file.filename.endswith('.pdf'):
            try:
                unique_filename = str(uuid.uuid4()) + ".pdf"
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(pdf_path)

                csv_filename = os.path.splitext(unique_filename)[0] + ".csv"
                csv_path = os.path.join(app.config['CSV_FOLDER'], csv_filename)

                text = extract_text(pdf_path)
                text = re.sub(r'(www\.)', r';\1', text) #insere ponto e virgula antes de urls que iniciam com www.

                lines = text.split('\n')
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    for line in lines:
                        line = corrigir_acentuacao(line)
                        row = line.split(';')
                        writer.writerow(row)

                qr_codes = extrair_qr_codes(pdf_path)
                qr_code_string = ", ".join(qr_codes) if qr_codes else "Nenhum QR Code encontrado"

                return render_template('index.html', csv_file=f"/{app.config['CSV_FOLDER']}/{csv_filename}", qr_codes=qr_code_string)
            except Exception as e:
                return render_template('index.html', error=f"An error occurred: {str(e)}")
        else:
            return render_template('index.html', error="Invalid file type. Only PDF files are allowed")

    return render_template('index.html')

@app.route('/csv_files/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['CSV_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)