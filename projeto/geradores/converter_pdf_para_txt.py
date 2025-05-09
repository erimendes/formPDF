import fitz  # PyMuPDF

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