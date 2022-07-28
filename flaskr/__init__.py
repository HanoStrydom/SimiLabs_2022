from ipaddress import summarize_address_range
import os, socket
from types import MethodDescriptorType

from flask import Flask, render_template, request,flash,redirect
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage


HOST = ''
PORT = 5000


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # delete if broken
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    path = os.getcwd()
    # file Upload
    UPLOAD_FOLDER = os.path.join(path, 'flaskr/templates/uploader')

    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'])

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # doesn't even have to be reachable
        s.bind((HOST,PORT))
    except Exception:
        return 'Error: server failed to startup ... could not find port number'
    finally:
        s.close()
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    # a simple page that says hello
    @app.route('/')
    def initial():
        return render_template('auth/login.html')
        #return f'Server is running on Port {PORT}'

    @app.route('/home')
    def home():
        return render_template('home/home.html')

    @app.route('/QuickText')
    def QuickText():
        return render_template('text/QuickText.html')

    
    @app.route('/ExtensiveText')
    def ExtensiveText():
        return render_template('text/ExtensiveText.html')


    @app.route('/stylometry')
    def stylo():
        return render_template('stylometry/stylo.html')

    @app.route('/reports')
    def report():
        return render_template('reports/report.html')

    @app.route('/help')
    def help():
        return render_template('help/help.html')

    # Upload File
    @app.route('/QuickText', methods=['GET','POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            file2 = request.files['file2']
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename2 = secure_filename(file2.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
                flash('File successfully uploaded')
                return redirect('/home')
            else:
                flash('Allowed file types are txt, pdf, docx')
                return redirect(request.url)

    # Upload Folder
    @app.route('/ExtensiveText', methods=['POST'])
    def upload_folder():
        if request.method == 'POST':

            if 'files[]' not in request.files:
                flash('No file part')
                return redirect(request.url)

            files = request.files.getlist('files[]')

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # this uploads second file
                    file2 = request.files['file2']
                    filename2 = secure_filename(file2.filename)
                    file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))


            flash('File(s) successfully uploaded')
            return redirect('/home')

    return app