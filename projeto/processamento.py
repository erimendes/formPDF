from geradores.utils import remover_caracteres_especiais

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

    questoes.sort(key=lambda q: q['cabecalho'].lower())
    return questoes
