from flask import Flask, request, render_template, url_for, redirect, flash, session, logging
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
import consulta_cep
import os
import json
from time import sleep
from functools import wraps

# Diretório padrão do projeto:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'}

# Configurando a instância inicial do Flask
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = '@123456'
# Configuração de upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configuração Mysql:
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'consulta_cep'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Iniciando meu banco:
mysql = MySQL(app)

# Upload de arquivo:


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Antes de carregar novos arquivos limpa o diretório de Upload


def limpa_diretorio():
    for _, _, files in os.walk(UPLOAD_FOLDER):
        for file in files:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, file))
            except OSError as e:
                print(f'Error: {e.strerror}')


def insert(tabela, *args):
    '''Essa função recebe um dicionário e faz
    uma inserção dinâmica convertendo as chaves do dict
    em campos de coluna para o banco e os valores em values'''

    # Cria campo de colunas do banco
    # colunas = tuple(args[0].keys())
    valores = tuple(args[0].values())
    # q = f'INSERT INTO {tabela} {colunas} VALUES {valores}'
    q = f'INSERT INTO {tabela} VALUES {valores};'

    # Monta a constula
    return q


def select(tabela, campo, *args):
    valores = tuple(args[0].values())
    q = f'SELECT * FROM {tabela} WHERE {campo} in {valores}'
    return q


def executa_acao_banco(q):
    app.logger.info(q)
    cur = mysql.connection.cursor()
    # cur.execute('''CREATE TABLE examplo (id INTEGER, nome VARCHAR(20))''')
    try:
        cur.execute(q)
        cur.connection.commit()
    except Exception as e:
        flash(f'{str(e)}', 'danger')
    # Fecha a conexão
    cur.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    limpa_diretorio()

    if request.method == 'POST':
        # Check if the past request has the file part
        if 'file' not in request.files:
            flash('Sem arquivos para upload.', 'primary')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Você não selecionou nenhum arquivo.', 'warning')
            return redirect(request.url)

        if file and not allowed_file(file.filename):
            flash('A extensão do arquivo selecionado, não é válida.', 'danger')

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
    # Lista de Ceps que serão consultados:
    for _, _, files in os.walk(UPLOAD_FOLDER):
        ceps = set(consulta_cep.carrega_dados_inicial()) # Converte para um set para remover duplicatas

    # Valida se a lista de ceps já foi consultada:
    cur = mysql.connect.cursor()
    cur.execute('SELECT cep FROM cep')
    lista_ceps_consultados = cur.fetchall()
    app.logger.info(lista_ceps_consultados)

    # Carrega o json para adicionar ou não um valor a ele:
    # with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), 'r', encoding='utf-8') as f:
    #     base_consolidada = json.load(f)

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
                ddd = dicionario['cidade']['ddd'] 
                if not ddd:
                    ddd = 0
                    
                dict_data = {
                    'cep': dicionario['cep'],
                    'estado': dicionario['estado']['sigla'] if 'estado' in dicionario.keys() else 'null',
                    'cidade': dicionario['cidade']['nome'] if 'cidade' in dicionario.keys() else 'null',
                    'ddd': ddd,
                    'logradouro': dicionario['logradouro'] if 'logradouro' in dicionario.keys() else 'null',
                    'bairro': dicionario['bairro'] if 'bairro' in dicionario.keys() else 'null'
                }
                # Executa insert no banco da lista consolidada:
                executa_acao_banco(insert('cep', dict_data))
            else:
                dict_data = {
                    'cep': cep,
                    'estado': 'NE',
                    'cidade': 'NE',
                    'ddd': 'NE',
                    'logradouro': 'NE',
                    'bairro': 'NE'
                }

            # Consolida a informação na lista geral:
            # base_consolidada.append(dict_data.copy())
            dict_data.clear()
            dicionario.clear()

    # Regrava os dados no json:
    # with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), 'w+', encoding='utf-8') as f:
    #     json.dump(base_consolidada, f, indent=4)

    # Retorna um json apenas com a consulta do usuário:
    # Fazer um select do que o usuário está consultando.
    # with open(os.path.join(BASE_DIR, 'ceps_consolidado.json'), 'r', encoding='utf-8') as f:
    #     filtrar = json.load(f)

    # consulta = []
    # for cep in ceps:
    #     for dado in filtrar:
    #         if int(dado['cep']) == int(cep):
    #             consulta.append(dado)

    # Salva um json com a consulta do usuário:
    # with open(os.path.join(BASE_DIR, 'consulta.json'), 'w+', encoding='utf-8') as f:
    #     json.dump(consulta, f, indent=4)

    # Cria o arquivo CSV que será enviado por email:
    consulta_cep.salva_csv()

    # Envia email
    # with open(os.path.join(BASE_DIR, 'dados_usuario.json'), 'r') as f:
    #     dict_usuario = json.load(f)

    # with open(os.path.join(TEMPLATE_DIR, 'mensagem_email.html'), 'r') as html:
    #     mensagem = html.read()

    # consulta_cep.envia_email(dict_usuario['email'],
    #                          'Resultado da sua consulta de CEPS', mensagem)

    flash('Tudo certo, agora é só aguardar o e-mail chegar na sua caixa de entrada', 'success')

    return render_template('index.html')

# Classe do formulário de registro


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=3, max=100)])
    username = StringField('Username', [validators.Length(min=4, max=45)])
    token = StringField('Token', [validators.Length(min=10, max=150)])
    email = StringField('Email', [validators.Length(min=6, max=120)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo(
                                              'confirm', message='Senha incorreta')
                                          ])
    confirm = PasswordField('Confirme a senha')

# Registro do usuário


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        token = form.token.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        flash(f'{name} {username} {token} {email} {password}')

        # Criando um cursor
        cur = mysql.connect.cursor()

        # Execute insert no banco
        cur.execute('''INSERT INTO usuarios(nome, usuario, token, email, senha) VALUES(%s, %s, %s, %s, %s)''', (
            name, username, token, email, password))

        # Commit
        mysql.connection.commit()

        # Fechando a conexão:
        cur.close()

        flash('Você foi registrado e já pode fazer login', 'success')

        return redirect(url_for('logar'))

    return render_template('registrar.html', form=form)


@app.route('/logar', methods=['GET', 'POST'])
def logar():
    if request.method == 'POST':
        # Obtém os campos do formulário
        username = request.form['username']
        password_candidato = request.form['password']

        # Cria o cursor
        cur = mysql.connection.cursor()

        # Obtém o usuário pelo nome
        result = cur.execute(
            "SELECT * FROM USUARIOS WHERE usuario = %s", [username])

        if result > 0:
            # Obtém o hash da senha:
            data = cur.fetchone()
            password = data['senha']

            # Compara as senhas:
            if sha256_crypt.verify(password_candidato, password):
                app.logger.info('PASSWORD CORRETO')
                # Passou
                session['logged_in'] = True
                session['username'] = username

                flash('Agora você está logado!', 'success')
                # return redirect(url_for('index.html'))
                return render_template('index.html')

            else:
                error = 'Usuário não encontrado'
                return render_template('logar.html', error=error)

        # Fecha a conexão
        cur.close()

    return render_template('logar.html')


# Checar se o usuário está logado
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Não autorizado, por favor faça login.', 'danger')
            return redirect(url_for('logar'))

    return wrap


@app.route('/sair')
def sair():
    session.clear()
    flash('Você deslogou-se da aplicação.', 'success')
    return redirect(url_for('logar'))


# Dados do usuário
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Cursor
    cur = mysql.connection.cursor()

    # Obtém dados do usuário
    result = cur.execute('''SELECT id, nome, email, token FROM usuarios WHERE usuario = %s''', [
                         session['username']])

    dados_usuario = cur.fetchall()

    # Fecha a conexão
    cur.close()

    if result > 0:
        app.logger.info(dados_usuario)
        return render_template('dashboard.html', dados_usuario=dados_usuario)
    else:
        msg = 'Dados do usuário não localizado'
        return render_template('dashboard.html', msg=msg)


@app.route('/sobre', methods=['GET'])
def sobre():
    return render_template('sobre.html')


if __name__ == '__main__':
    app.secret_key = '@123456'
    app.run(debug=True)
