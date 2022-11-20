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
import docx
import PyPDF2
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from PIL import Image
from wordcloud import WordCloud
from flaskr.quicksimilarity import calc_cosine_similarity,jaccard_similarity
from flaskr.extractmetadata import getMetaDataDoc,getMetaDataPDF, getRowColor
import json
from flask import send_from_directory

from fpdf import FPDF
from RunFastStylometry import fastStyle

from flaskr.countWords import countWords1,countWords2
from flaskr.Gensim import CreateStudent,UpdateStudent, CompareCorpus, DeleteStudent
from flaskr.createPDFStylo import WriteToPDFStylo
import shutil

# NB!!! Remember to gitignore the .env file!
load_dotenv()

HOST = ''
PORT = 5000

def create_app(test_config=None):
    try:
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
        UPLOAD_IMG = os.getenv('UPLOAD_IMG')
        UPLOAD_PDF = os.getenv('UPLOAD_PDF')
        UPLOAD_REPORT = os.getenv('UPLOAD_REPORT')
        UPLOAD_STYLO = os.getenv('UPLOAD_STYLO')
        UPLOAD_EXTENSIVE = os.getenv('UPLOAD_EXTENSIVE')
        HELP_PAGE = os.getenv('HELP_PAGE')
        HELP_PDF = os.getenv('HELP_PDF')
        
        
        app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
        app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
        app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
        app.config['MYSQL_DB'] = os.getenv('MySQL_DB')

        
        mysql = MySQL(app)

        # insert if uploading to folder
        # if not os.path.isdir(UPLOAD_FOLDER):
        #     os.mkdir(UPLOAD_FOLDER)

        app.config['UPLOAD_IMG'] = UPLOAD_IMG
        app.config['UPLOAD_PDF'] = UPLOAD_PDF
        app.config['UPLOAD_REPORT'] = UPLOAD_REPORT
        app.config['UPLOAD_STYLO'] = UPLOAD_STYLO
        app.config['UPLOAD_EXTENSIVE'] = UPLOAD_EXTENSIVE
        app.config['HELP_PAGE'] = HELP_PAGE
        app.config['HELP_PDF'] = HELP_PDF
        
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
    except Exception as e:
        return render_template("exceptions/errors.html", error = e)

    @app.after_request
    def after_request(response):
        try:
            """Disable caching"""
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/')
    def initial():
        try:
            return redirect('auth/authLogin')
            #return f'Server is running on Port {PORT}'
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/home')
    def home():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            return render_template('home/home.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)
    
    @app.route('/auth/authLogin',methods =['GET', 'POST'])
    def authLogin():
        try:
            session.clear()
            msg = ''
            if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
                username = request.form['username']
                password = request.form['password']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE username = %s', ([username]))
                account = cursor.fetchone()
                if account is None:
                    msg = 'Ivalid credentials!'
                elif not check_password_hash(account['password'], password):
                    msg = 'Invalid credentials!'
                if msg == '':
                    session['loggedin'] = True
                    session['id'] = account['id']
                    session['username'] = account['username']
                    msg = 'Logged in successfully!'
                    return render_template('/home/home.html', msg = msg)
            return render_template('auth/authLogin.html', msg=msg)
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)


    @app.route('/auth/authRegister', methods=('GET', 'POST'))
    def register():
        try:
            session.clear()
            msg = ''
            if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'password2' in request.form:
                username = request.form['username']
                password = request.form['password']
                password2 = request.form['password2']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM accounts WHERE username = % s', ([username]))
                account = cursor.fetchone()
                if account:
                    msg = 'Account already exists!'
                elif password != password2:
                    msg = 'Passwords do not match!'
                elif not username or not password or not password2:
                    msg = 'Please fill out the form!'
                else:
                    cursor.execute('INSERT INTO accounts VALUES (NULL,% s, % s)', ([username], [generate_password_hash(password)]))
                    mysql.connection.commit()
                    cursor.execute('SELECT * FROM accounts WHERE username = %s', ([username]))
                    account = cursor.fetchone()
                    session['loggedin'] = True
                    session['id'] = account['id']
                    session['username'] = account['username']
                    msg = 'Logged in successfully!'
                    return render_template('/home/home.html', msg = msg)
            elif request.method == 'POST':
                msg = 'Please fill out the form !'
            return render_template('auth/authRegister.html', msg=msg)
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/logout')
    def logout():
        try:
            # protecting your api endpoints
            for key in list(session.keys()):
                if session.key == "session":
                    session["session"].clear()
                session.pop(key)
            # response.delete_cookie('session')
            session.clear()
            print(f"Session: {session['session']}")
            return redirect(url_for('authLogin'))
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/QuickText')
    def QuickText():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            return render_template('text/QuickText.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/ExtensiveText')
    def ExtensiveText():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            return render_template('text/ExtensiveText.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/reports')
    def report():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            return render_template('reports/report.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/help')
    def help():
        try:
            path = os.getenv('HELP_PDF')
            # path = "C:/Users/Llewellyn/Desktop/SimiLabs_2022/flaskr/static/pdf/" 
            a = os.listdir(path)
            print(a)
            text = json.dumps(sorted(a))
            return render_template("help/help.html", contents = text) 
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    #Report Links Begin
    @app.route('/quickReport', methods=['GET'])
    def quickReport():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            return render_template('reports/quickReport.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/extensiveReport', methods=['GET'])
    def extensiveReport():
        try:
            return render_template('reports/extensiveReport.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/styloReport', methods=['GET'])
    def styloReport():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            return render_template('reports/styloReport.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/stylometry', methods=['GET','POST'])
    def stylo():
        try:
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            
            if request.method == 'POST':
                folder = "data/test"
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
                
                #code to convert a PDF to text file
                if not request.files["file1"]:
                    abort(400, "missing file")
                try:
                    name = request.form["studentname"]
                    print(name)
                    doc1 = request.files["file1"]
                    doc1.encoding = 'utf-8'
                    
                    # Extracting text from alleged document
                    if doc1.filename.endswith('.docx'):
                        filenamedoc = secure_filename(doc1.filename)
                        file1 = docx2txt.process(doc1)
                    elif doc1.filename.endswith('.pdf'):
                        pdfReader = PyPDF2.PdfFileReader(doc1)
                        count = pdfReader.numPages
                        file1 = ""
                        for i in range(count):
                            page = pdfReader.getPage(i)
                            file1 += page.extractText() 
                        filenamePDF = secure_filename(doc1.filename)
                    else:
                        filenametxt = secure_filename(doc1.filename)
                        doc1.seek(0)
                        file1 = doc1.read().decode("utf-8")
                    
                    #open text file
                    text_file = open("data/test/"+name+"_-_"+os.path.splitext(doc1.filename)[0]+".txt", "w", encoding="utf-8")
                    
                    #write string to file
                    text_file.write(file1)
                    
                    #close file
                    text_file.close()
                    fastStyle()
                    WriteToPDFStylo(name)
                    print(request.path)
                    return render_template('reports/styloReport.html')
            
                except Exception as e:
                    # abort(400, f"invalid file: {e}")
                    print(e)
            return render_template('stylometry/stylo.html')
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)


    # Upload File
    @app.route('/QuickText', methods=['GET','POST'])
    def compare():
        try:
            errMessage = ""
            if 'loggedin' not in session:
                return render_template('auth/authLogin.html')
            """Handle requests for /compare via POST"""
            # Read files
            if not request.files["file1"] or not request.files["file2"]:
                abort(400, "missing file")
            try:
                doc1 = request.files["file1"]
                doc2 = request.files["file2"]
                

                # Extracting text from alleged document
                if doc1.filename.endswith('.docx'):
                    filenamedoc = secure_filename(doc1.filename)
                    file1 = docx2txt.process(doc1)
                    file1Length = len(file1.split())
                elif doc1.filename.endswith('.pdf'):
                    pdfReader = PyPDF2.PdfFileReader(doc1)
                    count = pdfReader.numPages
                    file1 = ""
                    for i in range(count):
                        page = pdfReader.getPage(i)
                        file1 += page.extractText() 
                    filenamePDF = secure_filename(doc1.filename)
                    # file1 = pageObj.extractText()
                    file1Length = len(file1.split())
                else:
                    filenametxt = secure_filename(doc1.filename)
                    doc1.seek(0)
                    file1 = doc1.read().decode("utf-8")
                    file1Length = len(file1.split())
                
                # Extracting text from comparsion document
                if doc2.filename.endswith('.docx'):
                    docName = secure_filename(doc2.filename)
                    file2 = docx2txt.process(doc2)
                    file2Length = len(file2.split())
                elif doc2.filename.endswith('.pdf'):
                    pdfReader = PyPDF2.PdfFileReader(doc2)
                    count = pdfReader.numPages
                    file2 = ""
                    for i in range(count):
                        page = pdfReader.getPage(i)
                        file2 += page.extractText() 
                    pdfName = secure_filename(doc2.filename)
                    file2Length = len(file2.split())
                else:
                    txtName = secure_filename(doc2.filename)
                    doc2.seek(0)
                    file2 = doc2.read().decode("utf-8")
                    file2Length = len(file2.split())
                

            except Exception as e:
                abort(400, f"invalid file: {e}")

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
            
            #Word Cloud
            wordcloud = WordCloud().generate(file1)
            imgPath = os.getenv('UPLOAD_IMG')
            wordcloud.to_file(f"{imgPath}SimiLabs_2022/flaskr/static/images/WordCloud/wordcloud.png")  
            
            wordcloud2 = WordCloud().generate(file2)
            imgPath = os.getenv('UPLOAD_IMG')
            wordcloud2.to_file(f"{imgPath}SimiLabs_2022/flaskr/static/images/WordCloud/wordcloud2.png")       

            # Algorithms Description
            CosineTooltip = "The accuracy for this algorithm works better for smaller documents (<500 words)"
            JaccardTooltip = "The accuracy for this algorithm works better for bigger documents (>500 words)"


            # Calculate the similarity score between the two documents
            # Cosine Similarity
            percentageCosine = round(calc_cosine_similarity(file1, file2)[0]*100,2)
            colorCosine = calc_cosine_similarity(file1, file2)[1]
            # Jaccard Similarity 
            similarity = [file1,file2]
            similarity = [sentence.lower().split(" ") for sentence in similarity]
            percentageJaccard = round(jaccard_similarity(similarity[0], similarity[1])[0]*100,2)
            colorJaccard = jaccard_similarity(similarity[0], similarity[1])[1] 
            if doc1.filename.endswith('.docx'):
                docmeta = docx.Document(doc1)  
                metadata_dict = getMetaDataDoc(docmeta)
                meta_data = [metadata_dict["author"],metadata_dict["created"],
                metadata_dict["last_modified_by"],metadata_dict["modified"]]    
                rowColor = getRowColor(meta_data[0], meta_data[2])  
                # print(meta_data[0], " " ,meta_data[2], " " ,rowColor)
            elif doc1.filename.endswith('.pdf'): 
                doc1.save(os.path.join(app.config["UPLOAD_PDF"], doc1.filename))
                pdfPath = os.getenv('UPLOAD_PDF')+doc1.filename
                listMetaData = [getMetaDataPDF(pdfPath)[0],getMetaDataPDF(pdfPath)[1],
                getMetaDataPDF(pdfPath)[2],getMetaDataPDF(pdfPath)[3]]
                meta_data = listMetaData
                rowColor = getRowColor(meta_data[0], meta_data[2])  
                # print(meta_data[0], " " ,meta_data[2], " " ,rowColor)
            else: 
                meta_data = ["UNKNOWN","UNKNOWN","UNKNOWN","UNKNOWN"]
                rowColor = getRowColor(meta_data[0], meta_data[2])

            WriteToPDF(percentageJaccard, percentageCosine, meta_data[0], meta_data[2], meta_data[1], meta_data[3], doc1.filename)
            # pdfDownloadPath = f"{UPLOAD_REPORT}PlagiarismReport.pdf" 
            
            countWords1(file1)
            countWords2(file2)

            #Read content from file and store in variable
    
            CountWordstxt1 = open('./flaskr/WordCount/count.txt', 'r', encoding="utf8")
            CountWordstxt2 = open('./flaskr/WordCount/count2.txt', 'r', encoding="utf8")

            #Convert CountWords.txt to string
            CountWords1 = CountWordstxt1.read()
            CountWords2 = CountWordstxt2.read()

            return render_template("reports/quickReport.html", file1=highlights1, file2=highlights2, similarityJac=percentageJaccard,
            similarityCos=percentageCosine,colorCos=colorCosine, colorJac = colorJaccard , metadata = meta_data, rowColor = rowColor , 
            JaccardTooltip = JaccardTooltip, CosineTooltip = CosineTooltip,file1Length=file1Length, file2Length=file2Length, Test1 = CountWords1, Test2 = CountWords2)
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)
        
    def highlight(s, regexes):
        try:
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
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    def WriteToPDF(JacSim, CosSim, Creator, Modifier, createDate, ModDate, fileName):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size = 15)
        
            PlagJac = ""
            PlagCos = ""
            PlagCreate = ""
            
            if(JacSim > 30):
                PlagJac = "The student most likely plagiarized the document according to the Jaccard Similarity Score"
            else:
                PlagJac = "The student most likely did not plagiarize the document according to the Jaccard Similarity Score"    
            
            if(CosSim > 30):
                PlagCos = "The student most likely plagiarized the document according to the Cosine Similarity Score"
            else:
                PlagCos = "The student most likely did not plagiarize the document according \n to the Cosine Similarity Score"
                        
            if(Creator != Modifier):
                PlagCreate = "The student that created the document is not the same as the student that modified the document"
            else:
                PlagCreate = "The student that created the document is the same as the student that modified the document"
            
            pdf.multi_cell(200, 10, txt = "Plagiarism Report for: " + fileName, align = 'C')
            pdf.multi_cell(200, 10, txt = "Jaccard Similarity Score: " + str(JacSim), align = 'L')
            pdf.multi_cell(200, 10, txt = "Cosine Similarity Score: " + str(CosSim), align = 'L')
            pdf.multi_cell(200, 10, txt = "The student that created the document: " + str(Creator), align = 'L')
            pdf.multi_cell(200, 10, txt = "Date Created: " + str(createDate), align = 'L')
            pdf.multi_cell(200, 10, txt = "The student that last modified the document: " + str(Modifier), align = 'L')
            pdf.multi_cell(200, 10, txt = "Date Last Modified: " + str(ModDate), align = 'L')
            
            pdf.cell(200, 10, txt = " ", ln = 5, align = 'C')
            
            pdf.multi_cell(200, 10, txt = "Conclusion: ", align = 'C')
            pdf.multi_cell(200, 10, txt = str(PlagJac), align = 'L')
            pdf.multi_cell(200, 10, txt = str(PlagCos), align = 'L')
            pdf.multi_cell(200, 10, txt = str(PlagCreate), align = 'L')
            
            pdf.ln(200)
            
            pdf.cell(200, 10, txt = " ", ln = 1, align = 'C')
            pdf.cell(200, 10, txt = "Word Cloud Suspect", ln = 1, align = 'L')
            pdf.image(f"{os.getenv('UPLOAD_IMG')}SimiLabs_2022/flaskr/static/images/WordCloud/wordcloud.png", w = 100, h = 50)
            
            pdf.cell(200, 10, txt = " ", ln = 1, align = 'C')
            pdf.cell(200, 10, txt = "Word Cloud Suspect", ln = 1, align = 'L')
            pdf.image(f"{os.getenv('UPLOAD_IMG')}SimiLabs_2022/flaskr/static/images/WordCloud/wordcloud2.png", w = 100, h = 50)

            pdf.output(dest="F", name=UPLOAD_REPORT + "PlagiarismReport.pdf")
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)
        
    @app.route('/GenerateReport/<path:filename>', methods=['GET', 'POST'])
    def download(filename):
        try:
            # Appending app path to upload folder path within app root folder
            uploads = os.path.join(app.config['UPLOAD_REPORT'])
            # Returning file from appended path
            return send_from_directory(uploads, filename, as_attachment=True)
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.errorhandler(HTTPException)
    def errorhandler(error):
        """Handle errors"""
        return render_template("/reports/error.html", error=error), error.code
    for code in default_exceptions:
        app.errorhandler(code)(errorhandler)

    # Upload Folder
    @app.route('/ExtensiveText', methods=['GET','POST'])
    def upload_folder():
        try:
            if 'loggedin' not in session:
                    return render_template('auth/authLogin.html')
            if request.method == 'POST':
                # Clear the GensimTemp folder
                folder = "./flaskr/GensimTemp"
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
                
                stdNum = request.form['stdNum']
                doc1 = request.files["ExtensiveStudent"]
                doc1.save(os.path.join("./flaskr/GensimTemp/", doc1.filename))
                
                checked = request.form.getlist('extensiveBox')
                boolean = ""
                if(checked == ["extensiveBox"]):
                    boolean = "true"
                    print(boolean)

                ExtensiveFeedback = ""

                if request.form.get("ExtensiveText") == "CreateStudent":
                    print("Create Student")
                    CreateStudent(stdNum, doc1.filename)
                    ExtensiveFeedback = "Student " + str(stdNum) + " is created"
                elif request.form.get("ExtensiveText") == "UpdateStudent":
                    print("Compare Student")
                    UpdateStudent(stdNum, doc1.filename)
                    ExtensiveFeedback = "Student " + str(stdNum) + " is updated"
                elif request.form.get("ExtensiveText") == "CompareCorpus":
                    print("Compare Corpus")
                    extensiveList = CompareCorpus(stdNum, doc1.filename, boolean)
                    return render_template('reports/extensiveReport.html',theList=extensiveList)
            
                print(stdNum)
            
            return render_template('text/extensiveText.html', ExtensiveFeedback = ExtensiveFeedback)
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    @app.route('/DeleteStudent', methods=['POST'])
    def deleteStudent():
        ExtensiveFeedback = ""
        try:
            if 'loggedin' not in session:
                    return render_template('auth/authLogin.html')
            if request.method == 'POST':
                stdNum = request.form['dltStd']
                DeleteStudent(stdNum)
                ExtensiveFeedback = "Student " + str(stdNum) + " is deleted"
            return render_template('text/extensiveText.html', ExtensiveFeedback = ExtensiveFeedback)
        except Exception as e:
            return render_template("exceptions/errors.html", error = e)

    return app