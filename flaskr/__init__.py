from ipaddress import summarize_address_range
import os, socket
from types import MethodDescriptorType

import re
from flask import Flask, render_template, request,flash,redirect, url_for,abort, request 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import default_exceptions, HTTPException
from html import escape
import cs50
from flaskr.helpers import lines, sentences, substrings
import nltk
nltk.download('punkt')

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

    # insert if uploading to folder
    # if not os.path.isdir(UPLOAD_FOLDER):
    #     os.mkdir(UPLOAD_FOLDER)

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
    
    from . import db
    db.init_app(app)

    @app.after_request
    def after_request(response):
        """Disable caching"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    def initial():
        return redirect('auth/authLogin')
        #return f'Server is running on Port {PORT}'

    @app.route('/home')
    def home():
        return render_template('home/home.html')
    
    @app.route('/auth/authLogin')
    def authLogin():
        return render_template('auth/authLogin.html')

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
    # def upload_file():
    #     if request.method == 'POST':
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             flash('No file part')
    #             return redirect(request.url)
    #         file = request.files['file1']
    #         file2 = request.files['file2']
    #         if file.filename == '':
    #             flash('No file selected for uploading')
    #             return redirect(request.url)
    #         if file and allowed_file(file.filename):
    #             filename = secure_filename(file.filename)
    #             filename2 = secure_filename(file2.filename)
    #             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #             file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
    #             flash('File successfully uploaded')
    #             return redirect('/quickReport')
    #         else:
    #             flash('Allowed file types are txt, pdf, docx')
    #             return redirect(request.url)

    def compare():
        """Handle requests for /compare via POST"""
        # Read files
        if not request.files["file1"] or not request.files["file2"]:
            abort(400, "missing file")
        try:
            file1 = request.files["file1"].read().decode("utf-8")
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

        # Output comparison
        return render_template("reports/quickReport.html", file1=highlights1, file2=highlights2)

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
        return render_template("./templates/reports/error.html", error=error), error.code
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