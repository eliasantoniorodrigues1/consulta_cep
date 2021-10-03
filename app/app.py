from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug.utils import secure_filename
import consulta_cep
import os

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
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print('Upload realizado com sucesso!')
            file.save(full_path)
            flash('Arquivo carregado com sucesso!')
            return render_template('index.html', filename=filename.capitalize())
            # return redirect(url_for('download_file', name=filename))
    return render_template('index.html')
    # '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #     <input type=file name=file>
    #     <input type=submit value=Upload>
    # </form>
    # '''


if __name__ == '__main__':
    app.secret_key = '@123456'
    app.run(debug=True)
