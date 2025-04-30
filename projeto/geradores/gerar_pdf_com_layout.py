from fpdf import FPDF
import qrcode
import os
import shutil
from geradores.utils import remover_caracteres_especiais

def gerar_pdf_com_layout(questoes, nome_pdf):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    temp_dir = "qrcodes_temp"
    os.makedirs(temp_dir, exist_ok=True)

    pdf.add_page()

    for idx, questao in enumerate(questoes, start=1):
        qr_path = os.path.join(temp_dir, f"qrcode_{idx}.png")
        qr = qrcode.make(questao["link"])
        qr.save(qr_path)

        pdf.image(qr_path, x=10, y=pdf.get_y() + 5, w=20)
        pdf.set_xy(35, pdf.get_y() + 5)
        pdf.multi_cell(0, 8, f"{remover_caracteres_especiais(questao['link'])}\n"
                             f"{remover_caracteres_especiais(questao['cabecalho'])}\n"
                             f"{remover_caracteres_especiais(questao['subtitulo'])}")

        enunciado_formatado = f"{idx} - {questao['enunciado']}\n\n{questao.get('alternativas', '')}\n\n{questao.get('gabarito', '')}"
        texto_limpo = remover_caracteres_especiais(enunciado_formatado)
        pdf.set_x(10)
        pdf.multi_cell(0, 8, texto_limpo)

    pdf.output(nome_pdf)
    shutil.rmtree(temp_dir)
