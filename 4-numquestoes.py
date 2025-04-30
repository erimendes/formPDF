from flask import Flask, request, send_file, render_template_string
import qrcode
from fpdf import FPDF
import os
import shutil
import unicodedata
import json

app = Flask(__name__)

def remover_caracteres_especiais(texto):
    return unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')

def processar_txt(conteudo):
    questoes = []
    blocos = []
    bloco_atual = ""
    for linha in conteudo.strip().split("\n"):
        if linha.startswith("www.tecconcursos.com.br"):
            if bloco_atual:
                blocos.append(bloco_atual.strip())
            bloco_atual = linha + "\n"
        else:
            bloco_atual += linha + "\n"
    if bloco_atual:
        blocos.append(bloco_atual.strip())

    for bloco in blocos:
        linhas = bloco.strip().split("\n")
        if len(linhas) < 4:
            continue

        link = linhas[0].strip()
        cabecalho = linhas[1].strip()
        subtitulo = linhas[2].strip()
        corpo = "\n".join(linhas[3:]).strip()

        # Divide o corpo em enunciado, alternativas e gabarito
        gabarito = ""
        if "Gabarito:" in corpo:
            corpo, gabarito = corpo.rsplit("Gabarito:", 1)
            gabarito = "Gabarito: " + gabarito.strip()

        alternativas = []
        enunciado_linhas = []
        for linha in corpo.split("\n"):
            linha_strip = linha.strip()
            if any(linha_strip.lower().startswith(prefixo) for prefixo in ["a)", "b)", "c)", "d)", "e)", "certo", "errado"]):
                alternativas.append(linha_strip)
            else:
                enunciado_linhas.append(linha_strip)

        questoes.append({
            "link": link,
            "cabecalho": cabecalho,
            "subtitulo": subtitulo,
            "enunciado": " ".join(enunciado_linhas).strip(),
            "alternativas": "\r\n".join(alternativas).strip(),
            "gabarito": gabarito
        })

    questoes.sort(key=lambda q: q['cabecalho'].lower())  # ordena por cabecalho
    return questoes


def gerar_pdf_com_layout(questoes, nome_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    temp_dir = "qrcodes_temp"
    os.makedirs(temp_dir, exist_ok=True)

    pdf.add_page()

    for idx, questao in enumerate(questoes, start=1):
        # Gerar QR code
        qr_path = os.path.join(temp_dir, f"qrcode_{idx}.png")
        qr = qrcode.make(questao["link"])
        qr.save(qr_path)

        y_inicial = 20 + (idx - 1) * 150 # Ajuste a posição inicial vertical para cada questão

        # QR code à esquerda
        pdf.image(qr_path, x=10, y=pdf.get_y() + 5, w=20)

        # Cabeçalho e subtítulo à direita
        pdf.set_xy(35, pdf.get_y() + 5)
        pdf.multi_cell(0, 8, f"{remover_caracteres_especiais(questao['link'])}\n"
                                f"{remover_caracteres_especiais(questao['cabecalho'])}\n"
                                f"{remover_caracteres_especiais(questao['subtitulo'])}")

        # Enunciado + alternativas + gabarito
        enunciado_formatado = f"{idx} - {questao['enunciado']}\n\n{questao.get('alternativas', '')}\n\n{questao.get('gabarito', '')}"
        texto_limpo = remover_caracteres_especiais(enunciado_formatado)
        pdf.set_x(10)
        pdf.multi_cell(0, 8, texto_limpo)

    pdf.output(nome_pdf)
    shutil.rmtree(temp_dir)

def gerar_pdf_com_resposta(questoes, nome_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    temp_dir = "qrcodes_temp"
    os.makedirs(temp_dir, exist_ok=True)

    pdf.add_page()
    y = 20
    altura_por_questao = 80  # Ajuste conforme necessário para o espaçamento entre as questões

    for idx, questao in enumerate(questoes, start=1):
        # Gerar QR code
        qr_path = os.path.join(temp_dir, f"qrcode_{idx}.png")
        qr = qrcode.make(questao["link"])
        qr.save(qr_path)

        # Posição inicial para cada questão
        y_inicial = y

        # QR code à esquerda
        pdf.image(qr_path, x=10, y=y, w=20)

        # Cabeçalho e subtítulo à direita
        pdf.set_xy(35, y)
        pdf.multi_cell(0, 8, f"{remover_caracteres_especiais(questao['link'])}\n"
                                f"{remover_caracteres_especiais(questao['cabecalho'])}\n"
                                f"{remover_caracteres_especiais(questao['subtitulo'])}")
        y = pdf.get_y() + 5

        # Determinar alternativa correta
        alternativa_correta = ""
        gabarito = questao.get("gabarito", "").replace("Gabarito:", "").strip().lower()
        alternativas = [alt.strip() for alt in questao.get("alternativas", "").split("\n")]

        if any(alt.lower() in ['certo', 'errado'] for alt in alternativas):
            # Questão do tipo Certo/Errado
            for alt in alternativas:
                if alt.lower().startswith(gabarito):
                    alternativa_correta = alt
                    break
        else:
            # Questão com letras (a, b, c, d, e)
            for alt in alternativas:
                if alt.lower().startswith(f"{gabarito})") or alt.lower().startswith(f"{gabarito} )"):
                    alternativa_correta = alt
                    break

        # Montar enunciado e resposta
        enunciado_formatado = f"{idx} - {questao['enunciado']}\nAlternativa correta:\n{alternativa_correta}"
        texto_limpo = remover_caracteres_especiais(enunciado_formatado)
        pdf.set_x(10)
        pdf.multi_cell(0, 8, texto_limpo)
        y = pdf.get_y() + 10  # Espaço entre as questões

        # Adicionar nova página se não houver espaço suficiente para a próxima questão
        if y + altura_por_questao > pdf.h - pdf.b_margin:  # Correção aqui: b_margin
            pdf.add_page()
            y = 20

    pdf.output(nome_pdf)
    shutil.rmtree(temp_dir)

def gerar_json(questoes, nome_json):
    with open(nome_json, 'w', encoding='utf-8') as f:
        json.dump({"questoes": questoes}, f, ensure_ascii=False, indent=4)

def gerar_txt(questoes, nome_txt):
    with open(nome_txt, 'w', encoding='utf-8') as f:
        for idx, questao in enumerate(questoes, start=1):
            f.write(f"----------\n")
            f.write(f"{questao['link']}\n")
            f.write(f"{questao['cabecalho']}\n")
            f.write(f"{questao['subtitulo']}\n")
            f.write(f"{idx} - {questao['enunciado']}\n")
            f.write(f"{questao.get('alternativas', '')}\n")
            f.write(f"{questao.get('gabarito', '')}\n")
            f.write(f"----------\n\n")

@app.route('/')
def home():
    return render_template_string(open('indexnumquestoes.html', encoding='utf-8').read())

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

    # Gerar arquivos
    gerar_pdf_com_layout(questoes, 'questoes_com_layout.pdf')  # com todas as alternativas
    gerar_pdf_com_resposta(questoes, 'questoes_apenas_respostas.pdf')  # só com a resposta correta
    gerar_json(questoes, 'questoes.json')
    gerar_txt(questoes, 'questoes.txt')

    # Você pode escolher qual arquivo retornar, ou zipar todos
    return send_file('questoes_apenas_respostas.pdf', as_attachment=True, download_name='questoes_apenas_respostas.pdf')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
