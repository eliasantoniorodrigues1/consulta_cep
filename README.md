# Busca do CEP pelo número
### Dado um número de CEP busca os dados respectivos

GET https://www.cepaberto.com/api/v3/cep
Parametro aceito cep
Exemplo de busca pelos dados do CEP 01001000 em Python:

import requests

url = "https://www.cepaberto.com/api/v3/cep?cep=01001000"
# O seu token está visível apenas pra você
headers = {'Authorization': 'Obtenha sueu t'}
response = requests.get(url, headers=headers)

print(response.json())
Resultado
Para o exemplo anterior, o resultado será:

{"cidade": {"ibge": "3550308", "nome": "São Paulo", "ddd": 11}, "estado": {"sigla": "SP"}, "altitude": 760.0, "longitude": "-46.636", "bairro"

---
## Objetivo do Projeto:
Esse projeto tem como objetivo facilitar a vida do usuário e dar a ele uma ferramenta
que o possibilite consultar ceps de forma automática sem que ele tenha que fazer
esse trabalho manualmente.
 - Por limitações da API do site CEPaberto só poderá ser executado no máximo
  10 mil consultas no dia, com uma limitação de 1 segundo entre cada request, 
  para que o sistema não seja bloqueado como tentativa de derrubar o site.

 - Após a coleta dos dados na API o aplicativo irá consolidar as informações
  e irá enviar um email para o usuário, para que dessa forma o mesmo fique livre
  para fazer outras atividades.

  - Em um teste inicial o aplicativo executou 7 mil consultas em um intervalo de
  aproximadamente 4 horas.

  - Foi implementado uma melhoria para que antes de realizar a consulta seja validado
  se já não tenho dados desse CEP na minha base json, armazenada no servidor interno
  da aplicação, com isso a consulta desnecessária foi eliminada e quanto mais o
  sistema é usado, mais rápido ele ficará, pois a base é incremental.

  ## Modo de Usar:
  Para usar o sistema, basta carregar uma planilha em xlsx (Excel)
  para o sistema.
  - Essa planilha deve ser composta por apenas uma coluna, que é a coluna de CEP. 
  Não há a necessidade de tratar duplicadas e valores nulos ou
  inválidos, pois o sistema já faz essa tratativa, removendo tudo
  que não é dígito da base enviada.
  - Cadastrar um e-mail no campo e-mail
  - Após finalizar o upload do arquivo, basta clicar no botão de 
  Confirmar e o sistema irá iniciar o processo de consulta e ao final
  o usuário receberá um email contendo a planilha consolidada.