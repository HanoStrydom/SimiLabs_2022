from ipaddress import summarize_address_range
import os, socket
from pydoc import doc
from types import MethodDescriptorType

import re
from flask import Flask, render_template, request,flash,redirect, url_for,abort, request, session 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import default_exceptions, HTTPException
from html import escape
import cs50
from flaskr.helpers import lines, sentences, substrings
import nltk
nltk.download('punkt')
import docx2txt
import sys
import PyPDF2
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.wordcloud import create_wordcloud_from_file

load_dotenv()

HOST = ''
PORT = 5000

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    # delete if broken
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    # Gets the current directory
    # path = os.getcwd()
    # UPLOAD_FOLDER = os.path.join(path, os.getenv('UPLOAD_DIR'))
    UPLOAD_FOLDER = os.getenv('UPLOAD_DIR')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('MySQL_DB')
    mysql = MySQL(app)

    # insert if uploading to folder
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'])
    app.config["TEMPLATES_AUTO_RELOAD"] = True

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

    @app.after_request
    def after_request(response):
        """Disable caching"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    @app.route('/')
    def initial():
        return redirect('auth/authLogin')
        #return f'Server is running on Port {PORT}'

    @app.route('/home')
    def home():
        return render_template('home/home.html')
    
    @app.route('/auth/authLogin',methods =['GET', 'POST'])
    def authLogin():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            # db = get_db()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s', ([username]))
            account = cursor.fetchone()
            if account is None:
                msg = 'Incorrect username.'
            elif not check_password_hash(account['password'], password):
                msg = 'Incorrect password.'
            if msg == '':
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return render_template('/home/home.html', msg = msg)
        return render_template('auth/authLogin.html', msg=msg)

    @app.route('/logout')
    def logout():
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('authLogin'))

    @app.route('/auth/authRegister', methods=('GET', 'POST'))
    def register():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'password2' in request.form:
            username = request.form['username']
            password = request.form['password']
            password2 = request.form['password2']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = % s', ([username]))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif password != password2:
                msg = 'Passwords do not match!'
            elif not username or not password or not password2:
                msg = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO accounts VALUES (NULL,% s, % s)', ([username], [generate_password_hash(password)]))
                mysql.connection.commit()
                msg = 'You have successfully registered !'
                return render_template('/home/home.html', msg = msg)
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template('auth/authRegister.html', msg=msg)

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

    #Report Links Begin
    @app.route('/quickReport', methods=['GET'])
    def quickReport():
        return render_template('reports/quickReport.html')

    @app.route('/extensiveReport', methods=['GET'])
    def extensiveReport():
        return render_template('reports/extensiveReport.html')

    @app.route('/styloReport', methods=['GET'])
    def styloReport():
        return render_template('reports/styloReport.html')

    #Report Links End

    # Upload File
    @app.route('/QuickText', methods=['GET','POST'])
    def compare():
        """Handle requests for /compare via POST"""
        # Read files
        if not request.files["file1"] or not request.files["file2"]:
            abort(400, "missing file")
        try:
            doc1 = request.files["file1"]
            doc2 = request.files["file2"]

            #Code to convert files to text - Thank you copilot for the help
            if request.files["file1"].filename.endswith('.docx'):
                file1 = docx2txt.process(request.files["file1"])
                filenamedoc = secure_filename(doc1.filename)
                doc1.save(os.path.join(app.config['UPLOAD_FOLDER'], filenamedoc))
            elif request.files["file1"].filename.endswith('.pdf'):
                pdfReader = PyPDF2.PdfFileReader(request.files["file1"])
                pageObj = pdfReader.getPage(0)
                file1 = pageObj.extractText()
                filenamePDF = secure_filename(doc1.filename)
                doc1.save(os.path.join(app.config['UPLOAD_FOLDER'], filenamePDF))
            else:
                filenametxt = secure_filename(doc1.filename)
                doc1.save(os.path.join(app.config['UPLOAD_FOLDER'], filenametxt))
                file1 = request.files["file1"].read().decode("utf-8")

            if request.files["file2"].filename.endswith('.docx'):
                file2 = docx2txt.process(request.files["file2"])
                docName = secure_filename(doc2.filename)
                doc2.save(os.path.join(app.config['UPLOAD_FOLDER'], docName))
            elif request.files["file2"].filename.endswith('.pdf'):
                pdfReader = PyPDF2.PdfFileReader(request.files["file2"])
                pageObj = pdfReader.getPage(0)
                doc2 = pageObj.extractText()
                pdfName = secure_filename(doc2.filename)
                file2.save(os.path.join(app.config['UPLOAD_FOLDER'], pdfName))
            else:
                txtName = secure_filename(doc2.filename)
                doc2.save(os.path.join(app.config['UPLOAD_FOLDER'], txtName))
                file2 = request.files["file2"].read().decode("utf-8")
            

        except Exception:
            abort(400, "invalid file")

        # Compare files
        if not request.form.get("algorithm"):
            abort(400, "missing algorithm")
        elif request.form.get("algorithm") == "lines":
            regexes = [f"^{re.escape(match)}$" for match in lines(file1, file2)]
        elif request.form.get("algorithm") == "sentences":
            regexes = [re.escape(match) for match in sentences(file1, file2)]
        elif request.form.get("algorithm") == "substrings":
            if not request.form.get("length"):
                abort(400, "missing length")
            elif not int(request.form.get("length")) >= 0:
                abort(400, "invalid length")
            regexes = [re.escape(match) for match in substrings(
                file1, file2, int(request.form.get("length")))]
        else:
            abort(400, "invalid algorithm")

        # Highlight files
        highlights1 = highlight(file1, regexes)
        highlights2 = highlight(file2, regexes)
        argsFileName = doc1.filename
        image = create_wordcloud_from_file(f'{os.getenv("UPLOAD_DIR")}/{argsFileName}')

        # Output comparison
        return render_template("reports/quickReport.html", file1=highlights1, file2=highlights2, image=image)

    def highlight(s, regexes):
        """Highlight all instances of regexes in s."""

        # Get intervals for which strings match
        intervals = []
        for regex in regexes:
            if not regex:
                continue
            matches = re.finditer(regex, s, re.MULTILINE)
            for match in matches:
                intervals.append((match.start(), match.end()))
        intervals.sort(key=lambda x: x[0])

        # Combine intervals to get highlighted areas
        highlights = []
        for interval in intervals:
            if not highlights:
                highlights.append(interval)
                continue
            last = highlights[-1]

            # If intervals overlap, then merge them
            if interval[0] <= last[1]:
                new_interval = (last[0], interval[1])
                highlights[-1] = new_interval

            # Else, start a new highlight
            else:
                highlights.append(interval)

        # Maintain list of regions: each is a start index, end index, highlight
        regions = []

        # If no highlights at all, then keep nothing highlighted
        if not highlights:
            regions = [(0, len(s), False)]

        # If first region is not highlighted, designate it as such
        elif highlights[0][0] != 0:
            regions = [(0, highlights[0][0], False)]

        # Loop through all highlights and add regions
        for start, end in highlights:
            if start != 0:
                prev_end = regions[-1][1]
                if start != prev_end:
                    regions.append((prev_end, start, False))
            regions.append((start, end, True))

        # Add final unhighlighted region if necessary
        if regions[-1][1] != len(s):
            regions.append((regions[-1][1], len(s), False))

        # Combine regions into final result
        result = ""
        for start, end, highlighted in regions:
            escaped = escape(s[start:end])
            if highlighted:
                result += f"<span class='highlight'>{escaped}</span>"
            else:
                result += escaped
        return result


    @app.errorhandler(HTTPException)
    def errorhandler(error):
        """Handle errors"""
        return render_template("/reports/error.html", error=error), error.code
    for code in default_exceptions:
        app.errorhandler(code)(errorhandler)

    # Upload Folder
    @app.route('/ExtensiveText', methods=['GET','POST'])
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
                    comparison = request.files['comparison']
                    filename3 = secure_filename(comparison.filename)
                    comparison.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
            return redirect('/extensiveReport')

    return app