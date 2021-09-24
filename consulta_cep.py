import requests
import re



cep = "32187120"
url = f"https://www.cepaberto.com/api/v3/cep?cep={cep}"
# O seu token está visível apenas pra você
headers = {'Authorization': 'Token token=b307af069f8f5e60c4c03be00251e29b'}
response = requests.get(url, headers=headers)

print(response.json())