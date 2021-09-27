import requests
import re
import pandas as pd
import json
from time import sleep


def carrega_dados_plan():
    # Pego a coluna de CEP da base da Michele:
    df = pd.read_excel('AUTOCERTO_2021.XLSX')
    ceps = df.iloc[:, -2].dropna().drop_duplicates()
    return list(ceps)


def consulta_cep(cep: str):
    cep = remove_non_digit(cep)
    url = f"https://www.cepaberto.com/api/v3/cep?cep={cep}"

    # O seu token está visível apenas pra você
    headers = {'Authorization': 'Token token=...'}
    r = requests.get(url, headers=headers)
    try:
        return r.json()
    except Exception:
        return {}


def remove_non_digit(string: str):
    return re.sub(r'\D', '', string)[:8]


if __name__ == '__main__':

    ceps = carrega_dados_plan()
    # ceps = ['32187120', '30190060', '32210700']
    dados_cep = []
    print(f'Coletando dados dos ceps...')
    for i, cep in enumerate(ceps):
        # O intervalo entre cada request tem que ser
        # de 1 segundo senão o site bloqueia:
        # Máximo de 10 mil consultas por dia.
        sleep(1.5)
        print(f'CEP: {cep}')
        dicionario = dict(consulta_cep(str(cep)))
        print(f'Resultado da busca: {dicionario}')

        # Se retornar alguma coisa na pesquisa salva:
        if dicionario:
            # Cria o dicionário com os valores que desejo do json:
            dict_data = {
                'cep': dicionario['cep'] if 'cep' in dicionario.keys() else 'NE',
                'estado': dicionario['estado']['sigla'] if 'estado' in dicionario.keys() else 'NE',
                'cidade': dicionario['cidade']['nome'] if 'cidade' in dicionario.keys() else 'NE',
                'ddd': dicionario['cidade']['ddd'] if 'cep' in dicionario.keys() else 'NE',
                'logradouro': dicionario['logradouro'] if 'logradouro' in dicionario.keys() else 'NE'
            }
        else:
            dict_data = {
                'cep': cep,
                'estado': 'NE',
                'cidade': 'NE',
                'ddd': 'NE',
                'logradouro': 'NE'
            }

        # Consolida a informação na lista geral:
        with open('ceps_consolidados.json', 'a+', encoding='utf-8') as f:
            f.write(json.dumps(dict_data, indent=4))
        # dados_cep.append(dict_data.copy())
        dict_data.clear()
        dicionario.clear()
    print(dados_cep)
