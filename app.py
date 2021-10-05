from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug.utils import secure_filename
import consulta_cep
import os
import json
from time import sleep

# Diretório padrão do projeto:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}

# Configurando a instância inicial do Flask
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Upload de arquivo:
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the past request has the file part
        print(request.files)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Você não selecionou nenhum arquivo.', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            flash('Arquivo carregado com sucesso!', 'success')

            # cria dicionário para armazernar os dados da consulta:
            dict_dados_usuario = {
                "filename": filename,
            }
            # Grava em um json os dados do usuário:
            with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'w+') as f:
                json.dump(dict_dados_usuario, f, indent=4)

            return render_template('index.html', filename=filename.capitalize())

    return render_template('index.html')


@app.route('/executar-consulta', methods=['POST', 'GET'])
def executar_consulta():
    # Coleto o email digitado pelo usuário
    email = request.form['email_input']
    with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'r') as f:
        dict_usuario = json.load(f)
        dict_usuario['email'] = email

    # Salva dados do usuário no json:
    with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'w+') as f:
        json.dump(dict_usuario, f, indent=4)

    # Lista de Ceps que serão consultados:
    ceps = consulta_cep.carrega_dados_inicial(
        os.path.join(UPLOAD_FOLDER, dict_usuario['filename']))

    # Valida se a lista de ceps já foi consultada:
    lista_ceps_consultados = consulta_cep.consulta_cep_consolidado()

    # Carrega o json para adicionar ou não um valor a ele:
    with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), 'r', encoding='utf-8') as f:
        base_consolidada = json.load(f)

    for i, cep in enumerate(ceps):
        # Valida se será necessário realizar o request do cep
        if cep in lista_ceps_consultados:
            continue
        else:
            # O intervalo entre cada request tem que ser
            # de 1 segundo senão o site bloqueia:
            # Máximo de 10 mil consultas por dia.
            sleep(1.1)

            dicionario = dict(consulta_cep.consulta_cep(str(cep)))

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
            base_consolidada.append(dict_data.copy())
            dict_data.clear()
            dicionario.clear()

    # Regrava os dados no json:
    with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), 'w+', encoding='utf-8') as f:
        json.dump(base_consolidada, f, indent=4)

    # Retorna um json apenas com a consulta do usuário:
    with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), 'r', encoding='utf-8') as f:
        filtrar = json.load(f)

    consulta = []
    for cep in ceps:
        for dado in filtrar:
            if int(dado['cep']) == int(cep):
                consulta.append(dado)

    # Salva um json com a consulta do usuário:
    with open(os.path.join(BASE_DIR, 'consulta.json'), 'w+', encoding='utf-8') as f:
        json.dump(consulta, f, indent=4)

    # Cria o arquivo CSV que será enviado por email:
    consulta_cep.salva_csv()

    # Envia email
    with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'r') as f:
        dict_usuario = json.load(f)

    with open(os.path.join(TEMPLATE_DIR, 'mensagem_email.html'), 'r') as html:
        mensagem = html.read()

    consulta_cep.envia_email(dict_usuario['email'],
                             'Resultado da sua consulta de CEPS', mensagem)

    flash('Tudo certo, agora é só aguardar o e-mail chegar na sua caixa de entrada', 'success')

    return render_template('index.html')


if __name__ == '__main__':
    # app.secret_key = '@123456'
    # app.run(debug=True)
    ...