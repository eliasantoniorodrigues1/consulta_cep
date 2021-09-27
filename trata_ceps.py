import json
import csv
from os import sep

with open('ceps_consolidado.json', encoding='utf-8') as f:
    dados = json.load(f)

    with open('CEPS_CONSOLIDADO.CSV', 'w+', encoding='utf-8') as arq:
        cabecalhos = list(dados[0].keys())
        w = csv.DictWriter(arq, fieldnames=cabecalhos, lineterminator='\n')
        w.writeheader()
        for dado in dados:
            print(dado)
            w.writerow(dado)
