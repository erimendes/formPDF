from fpdf import FPDF
import qrcode
import os
import shutil
from geradores.utils import remover_caracteres_especiais

def gerar_pdf_com_resposta(questoes, nome_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    temp_dir = "qrcodes_temp"
    os.makedirs(temp_dir, exist_ok=True)

    pdf.add_page()
    y = 20
    altura_por_questao = 80

    for idx, questao in enumerate(questoes, start=1):
        qr_path = os.path.join(temp_dir, f"qrcode_{idx}.png")
        qr = qrcode.make(questao["link"])
        qr.save(qr_path)

        pdf.image(qr_path, x=10, y=y, w=20)
        pdf.set_xy(35, y)
        pdf.multi_cell(0, 8, f"{remover_caracteres_especiais(questao['link'])}\n"
                             f"{remover_caracteres_especiais(questao['cabecalho'])}\n"
                             f"{remover_caracteres_especiais(questao['subtitulo'])}")
        y = pdf.get_y() + 5

        gabarito = questao.get("gabarito", "").replace("Gabarito:", "").strip().lower()
        alternativas = [alt.strip() for alt in questao.get("alternativas", "").split("\n")]

        alternativa_correta = ""
        if any(alt.lower() in ['certo', 'errado'] for alt in alternativas):
            for alt in alternativas:
                if alt.lower().startswith(gabarito):
                    alternativa_correta = alt
                    break
        else:
            for alt in alternativas:
                if alt.lower().startswith(f"{gabarito})") or alt.lower().startswith(f"{gabarito} )"):
                    alternativa_correta = alt
                    break

        enunciado_formatado = f"{idx} - {questao['enunciado']}\nAlternativa correta:\n{alternativa_correta}"
        texto_limpo = remover_caracteres_especiais(enunciado_formatado)
        pdf.set_x(10)
        pdf.multi_cell(0, 8, texto_limpo)
        y = pdf.get_y() + 10

        if y + altura_por_questao > pdf.h - pdf.b_margin:
            pdf.add_page()
            y = 20

    pdf.output(nome_pdf)
    shutil.rmtree(temp_dir)
