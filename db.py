from flask import Flask, logging
from flask_mysqldb import MySQL
import os
import requests



def consulta_cep(cep: str):
    # cep = remove_non_digit(cep)
    url = f"https://www.cepaberto.com/api/v3/cep?cep={cep}"

    # O seu token está visível apenas pra você
    headers = {'Authorization': 'Token token=b307af069f8f5e60c4c03be00251e29b'}
    r = requests.get(url, headers=headers)
    try:
        return r.json()
    except Exception:
        return {}
# app = Flask(__name__)

# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_DB'] = 'consulta_cep'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# mysql = MySQL(app)


# def insert(tabela, *args):
#     '''Essa função recebe um dicionário e faz
#     uma inserção dinâmica convertendo as chaves do dict
#     em campos de coluna para o banco e os valores em values'''
#     # Cria campo de colunas do banco
#     valores = tuple(args[0].values())
#     # q = f'INSERT INTO {tabela} {colunas} VALUES {valores}'
#     q = f'INSERT INTO {tabela} VALUES {valores};'

#     # Monta a constula
#     return q


# @app.route('/')
# def index():
#     dict_teste = {'cep': 32187120,
#                   'estado': 'MG',
#                   'cidade': 'Contagem',
#                   'ddd': 31,
#                   'logradouro': 'Rua caiçaras',
#                   'bairro': 'Xangrila'}
#     q = insert('cep', dict_teste)

#     app.logger.info(q)

#     cur = mysql.connection.cursor()
#     # cur.execute('''CREATE TABLE examplo (id INTEGER, nome VARCHAR(20))''')
#     cur.execute(q)
#     cur.connection.commit()

#     # Fecha a conexão
#     cur.close()

#     return 'Feito!'


# if __name__ == '__main__':
#     app.secret_key = '123456'
#     app.run(debug=True)
d = {"cidade": {"ibge": "3550308", "nome": "São Paulo", "ddd": 11}, "estado": {"sigla": "SP"}, "altitude": 760.0, "longitude": "-46.636",
     "bairro": "Sé", "complemento": "- lado ímpar", "cep": "01001000", "logradouro": "Praça da Sé", "latitude": "-23.5479099981"}
print(consulta_cep('78250000'))