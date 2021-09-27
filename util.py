import socket
import sys
import unicodedata
import re
import getpass
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import json
import os
import csv


def remove_acentos(string):
    normalizado = unicodedata.normalize('NFKD', string)

    return ''.join([c for c in normalizado if not unicodedata.combining(c)])


def remove_non_digit(str):
    return re.sub(r'\D', '', str)


def grava_log(caminho_completo, conteudo):
    with open(caminho_completo, 'w') as file:
        if conteudo != '':
            for linha in conteudo:
                file.write(linha)
                file.write('\n')
        else:
            file.write('Não há chapas para exclusao.')
            file.write('\n')


def dados_sessao_windows():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    user = getpass.getuser()
    return hostname, local_ip, user


def cria_csv(nome, lista_cabecalho, conteudo):
    ...


def data_agora_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def envia_email(to, subject, messsage, filename=None, imagem=None, frm=None, host='mail.grupoaec.com.br', port=2525, password=None):

    LOG_DIR = os.path.join(BASE_DIR, 'log')

    msg = MIMEMultipart()
    msg['from'] = frm
    msg['to'] = to
    msg['cc'] = 'aecrhpontomatriz@aec.com.br;aec.uipath@aec.com.br'
    msg['subject'] = subject

    with open(os.path.join(LOG_DIR, filename), 'r') as file:
        attachment = MIMEText(file.read())
        attachment.add_header('Content-Disposition',
                              'attachment', filename=filename)

    corpo = MIMEText(messsage, 'html')
    msg.attach(corpo)

    # Tratando a imagem
    with open(imagem, 'rb') as img:
        email_image = MIMEImage(img.read())
        email_image.add_header('Content-ID', '<imagem>')
        msg.attach(email_image)

    with smtplib.SMTP(host=host, port=port) as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(login, password)
            smtp.send_message(msg)
        except Exception as e:
            print('Email não enviado...')
            print('Erro:', e)


def salva_arquivo_json(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4, sort_keys=False)


def limpa_clipboard():
    if sys.platform == 'win32':
        import win32clipboard as clip
        clip.OpenClipboard()
        clip.EmptyClipboard()
        clip.CloseClipboard()
    elif sys.platform.startswith('linux'):
        import subprocess
        proc = subprocess.Popen(('xsel', '-i', '-b', '-1', '/dev/null'),
                                stdin=subprocess.PIPE)
        proc.stdin.close()
        proc.wait()
    else:
        raise RuntimeError(
            'Plataforma não suportada para limpar memória de items copiados.')


def le_json(arquivo: str):
    with open(arquivo, encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    return dados


def atualiza_json(arq: str, chave: str, lista: list):
    with open(arq, 'r+') as file:
        data = json.load(file)
        data[chave] = lista
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def dict_to_csv(nome):
    with open(f'{nome}.csv', 'w+', encoding='utf-8') as f:
        dados = json.load(path_file)
        w = csv.DictWriter(f, dados[0].keys())
        for dado in dados:
            w.writerow(dado)


if __name__ == '__main__':
    texto = 'EÇOALHO caroço até joão avô'
    print(remove_acentos(texto))
