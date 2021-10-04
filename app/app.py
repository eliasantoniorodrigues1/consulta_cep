from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug.utils import secure_filename
import consulta_cep
import os
import json

# Diretório padrão do projeto:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}

# Configurando a instância inicial do Flask
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# @app.route('/')
# def index():
#     return render_template('index.html')

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


@app.route('/executar_consulta', methods=['GET', 'POST'])
def executar_consulta():
    # Coleto o email digitado pelo usuário
    email = str(request.form['email_input'])
    with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'r') as f:
        dict_usuario = json.load(f)
        dict_usuario['email'] = email

    flash(dict_usuario)

    with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'w+') as f:
        json.dump(dict_usuario, f, indent=4)

    flash(os.path.join(UPLOAD_FOLDER, dict_usuario['filename']))

    lista_ceps_usuario = consulta_cep.carrega_dado_inicial(os.path.join(
        UPLOAD_FOLDER, dict_usuario['filename']))

    flash(lista_ceps_usuario)
    return render_template('index.html')


if __name__ == '__main__':
    app.secret_key = '@123456'
    app.run(debug=True)
