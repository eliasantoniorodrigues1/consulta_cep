# Busca do CEP pelo número
### Dado um número de CEP busca os dados respectivos

GET https://www.cepaberto.com/api/v3/cep
Parametro aceito cep
Exemplo de busca pelos dados do CEP 01001000 em Python:

import requests

url = "https://www.cepaberto.com/api/v3/cep?cep=01001000"
# O seu token está visível apenas pra você
headers = {'Authorization': 'Obtenha seu token aqui: https://cepaberto.com'}
response = requests.get(url, headers=headers)

print(response.json())
Resultado
Para o exemplo anterior, o resultado será:

{"cidade": {"ibge": "3550308", "nome": "São Paulo", "ddd": 11}, "estado": {"sigla": "SP"}, "altitude": 760.0, "longitude": "-46.636", "bairro"
