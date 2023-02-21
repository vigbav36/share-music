import os
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate, migrate
import uuid
 
# Settings for migrations


from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
migrate = Migrate(app, db)

Session(app)

UPLOAD_FOLDER = os.path.join(basedir, 'songs')
ALLOWED_EXTENSIONS = {'mp3'}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(80), unique=True, nullable=False)
    bio = db.Column(db.Text)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.name} email {self.email}>'

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100),unique=True ,nullable=False)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    file_loc = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Song {self.title} artist {self.artist}>'

@app.route('/')
def index():
    songs = Song.query.all()
    return render_template('index.html',songs=songs)
    
@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        user = User.query.filter_by(email=user_email).all()[0]
        if(user.password == user_password):
            session["name"] = user.name
            return redirect("/")
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload',methods=["POST","GET"])
def upload():
    if request.method == "POST":
        id = uuid.uuid1()
        file_loc = os.path.join(UPLOAD_FOLDER, str(id)+".mp3")

        song = Song(
            id = id,
            url = "/play/"+str(id),
            title = request.form.get("title"),
            artist = request.form.get("artist"),
            user = session["name"],
            album= request.form.get("album"),
            file_loc = file_loc
        )
        
        if 'file' not in request.files:
            print("err1")
            return redirect(request.url)

        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            print("err2")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            file.save(file_loc)
            return render_template("index.html")
    else:
        return render_template("upload.html")
        



