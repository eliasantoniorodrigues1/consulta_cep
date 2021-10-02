import json

with open('teste.json', 'r') as f:
    dados = json.load(f)

ceps = []
for dado in dados:
    ceps.append(dado['cep'])

print(ceps)