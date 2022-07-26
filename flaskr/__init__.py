import os, socket

from flask import Flask, render_template

HOST = ''
PORT = 5000

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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
        return render_template('auth/register.html')
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

    

    return app