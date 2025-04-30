
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
