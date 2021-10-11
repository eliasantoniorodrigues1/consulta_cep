import requests
import re
import pandas as pd
import json
# from time import sleep
import os
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
# from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


def carrega_dados_inicial():
    # Pego a coluna de CEP da base da Michele:
    for _, _, files in os.walk(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, files[0])
        _, extensao = os.path.splitext(files[0])

    if 'xls' in extensao:
        df = pd.read_excel(file_path)
        ceps = df.iloc[:, 0].dropna().drop_duplicates()
    else:
        df = pd.read_csv(file_path)
        ceps = df.iloc[:, 0].dropna().drop_duplicates()

    return list(ceps)


def consulta_cep(cep: str):
    cep = remove_non_digit(cep)
    url = f"https://www.cepaberto.com/api/v3/cep?cep={cep}"

    # O seu token está visível apenas pra você
    headers = {'Authorization': 'Token token=b307af069f8f5e60c4c03be00251e29b'}
    r = requests.get(url, headers=headers)
    try:
        return r.json()
    except Exception:
        return {}


def consulta_cep_consolidado():
    # Nome padrão do arquivo de consolidação:
    # Sem duplicidades
    with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), encoding='utf-8') as f:
        dados = json.load(f)

    ceps = []
    for dado in dados:
        if 'cep' in dado.keys():
            ceps.append(int(remove_non_digit(str(dado['cep']))))

    # Ordena a lista
    ceps_ordenados = sorted(ceps)

    # Remove Duplicados
    ceps_ordenados = list(set(ceps_ordenados))

    return ceps_ordenados


def remove_non_digit(string: str):
    return re.sub(r'\D', '', string)[:8]


def salva_csv():
    # with open(os.path.join(BASE_DIR, 'consulta.json'), encoding='utf-8') as f:
    #     dados = json.load(f)

    # with open(os.path.join(BASE_DIR, 'Resultado_Consulta_Cep.CSV'), 'w+', encoding='utf-8') as arq:
    #     cabecalhos = list(dados[0].keys())
    #     w = csv.DictWriter(arq, fieldnames=cabecalhos, lineterminator='\n')
    #     w.writeheader()
    #     for dado in dados:
    #         w.writerow(dado)
    ...

def envia_email(to, subject, messsage, filename=None, imagem=None, frm=None, host='smtp.gmail.com', port=587, password=None):

    msg = MIMEMultipart()
    msg['from'] = frm
    msg['to'] = to
    msg['subject'] = subject

    corpo = MIMEText(messsage, 'html')
    msg.attach(corpo)

    filename = 'Resultado_Consulta_Cep.csv'
    attachment = open(os.path.join(
        BASE_DIR, 'Resultado_Consulta_Cep.csv'), 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    "attachment; filename= %s" % filename)

    msg.attach(part)

    attachment.close()

    # Tratando a imagem
    # with open(imagem, 'rb') as img:
    #     email_image = MIMEImage(img.read())
    #     email_image.add_header('Content-ID', '<imagem>')
    #     msg.attach(email_image)

    with smtplib.SMTP(host=host, port=port) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(frm, password)
            smtp.send_message(msg)
        except Exception as e:
            print('Email não enviado...')
            print('Erro:', e)


if __name__ == '__main__':
    ...
