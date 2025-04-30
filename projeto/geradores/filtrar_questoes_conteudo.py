def filtrar_questoes_conteudo(conteudo):
    linhas = conteudo.splitlines()
    questoes_filtradas = []

    for linha in linhas:
        linha_limpa = linha.strip()

        # Ignorar numeração de páginas tipo "1/", "2/", etc.
        if linha_limpa.startswith(('1/', '2/', '3/', '4/', '5/', '31/01/')):
            continue

        # Ignorar números sozinhos
        if linha_limpa.isdigit():
            continue

        # Ignorar linhas como "5)", "6)", etc.
        if linha_limpa.endswith(')') and linha_limpa[:-1].isdigit():
            continue

        # Ignorar marca d'água do site
        if 'Tec Concursos - Questões para concursos' in linha_limpa:
            continue

        # Ignorar links do Tec Concursos
        if 'https://www.tecconcursos.com.br/questoes/cadernos/' in linha_limpa:
            continue

        # Ignorar linhas tipo "30/30", "29/30", etc.
        if '/' in linha_limpa and linha_limpa.replace('/', '').isdigit():
            continue

        # Se passou por todos os filtros, adiciona
        questoes_filtradas.append(linha)

    return '\n'.join(questoes_filtradas)