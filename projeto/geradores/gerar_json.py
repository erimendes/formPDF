import json

def gerar_json(questoes, nome_json):
    with open(nome_json, 'w', encoding='utf-8') as f:
        json.dump({"questoes": questoes}, f, ensure_ascii=False, indent=4)
