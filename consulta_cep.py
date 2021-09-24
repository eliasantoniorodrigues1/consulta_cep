import requests
import re



cep = "32187120"
url = f"https://www.cepaberto.com/api/v3/cep?cep={cep}"
# O seu token está visível apenas pra você
headers = {'Authorization': 'Token token=...'}
response = requests.get(url, headers=headers)

print(response.json())
