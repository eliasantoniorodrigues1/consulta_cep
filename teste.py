import json

with open('ceps_consolidado.json', 'r') as f:
    lista = json.load(f)

with open('ceps_consolidao_unico.json', 'w+') as f:
    visto = set()
    lista_dict_unico = []
    for dicionario in lista:
        dados_tupla = tuple(dicionario.items())
        if dados_tupla not in visto:
            visto.add(dados_tupla)
            lista_dict_unico.append(dicionario)
    
    json.dump(lista_dict_unico, f, indent=4)

print(lista_dict_unico)