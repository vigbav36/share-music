import os
from flask import Flask, jsonify, render_template, request, url_for, redirect, session, flash, send_from_directory
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


@app.route('/song/<path:filename>')
def song(filename):
    filename = os.path.basename(filename)
    print(filename)
    return send_from_directory(UPLOAD_FOLDER, filename)


class User(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(80), unique=True, nullable=False)
    bio = db.Column(db.Text)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.name} email {self.email}>'

class Song(db.Model):
    id = db.Column(db.String(500), primary_key=True)
    url = db.Column(db.String(500),unique=True ,nullable=False)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    file_loc = db.Column(db.String(600), nullable=False)

    def __repr__(self):
        return f'<Song {self.title} artist {self.artist}>'

@app.route('/')
def index():
    songs = Song.query.all()
    return render_template('index.html',songs=songs,search=False)
    
@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        user = User.query.filter_by(email=user_email).all()[0]
        if(user.password == user_password):
            session['name'] = user.name
            session['id'] = user.id
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
        
        if 'file' not in request.files:
            print("err1")
            return redirect(request.url)

        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            print("err2")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            
            id = str(uuid.uuid1().hex)
            file_loc = os.path.join(UPLOAD_FOLDER, str(id)+".mp3")
            file.save(file_loc)
            try:
                song = Song(
                    id = id,
                    url = str("/play/"+str(id)),
                    title = str(request.form.get("title")),
                    artist = str(request.form.get("artist")),
                    user = str(session["id"]),
                    album= str(request.form.get("album")),
                    file_loc = str(file_loc)
                )
                db.session.add(song)
                db.session.commit()

            except Exception as e: print(e)
            
            print(song.url," ",song.file_loc)
            return index()
    else:
        return render_template("upload.html")
        
@app.route("/search", methods=["POST","GET"])
def search():
    if request.method == "POST":

        search_query = request.form.get("search")

        if search_query=="":
            return index()
       
        exact_match_title = Song.query.filter_by(title=search_query).all()
        exact_match_artist = Song.query.filter_by(artist=search_query).all()
        exact_match_album = Song.query.filter_by(album=search_query).all()

        if len(exact_match_title) == 0:
            close_match_title = Song.query.filter(Song.title.op('regexp')(rf'[.]*{search_query}[.]*')).all()
            songs_title=close_match_title

        else:
            songs_title=exact_match_title
        
        if len(exact_match_artist) == 0:
            close_match_artist = Song.query.filter(Song.artist.op('regexp')(rf'[.]*{search_query}[.]*')).all()
            songs_artist=close_match_artist
        else:
            songs_artist=exact_match_artist

        if len(exact_match_album) == 0:
            close_match_album = Song.query.filter(Song.album.op('regexp')(rf'[.]{search_query}[.]*')).all()
            songs_album=close_match_album
        else:
            songs_album=exact_match_album

        return render_template("index.html",songs_title=songs_title,songs_artist=songs_artist,songs_album=songs_album,search=True)

@app.route('/play/<song_id>')
def play(song_id):
    song = Song.query.filter_by(id=song_id).all()
    if len(song) == 0:
        return jsonify({'message': f':File has been deleted or removed'}), 500
    else:
        return render_template("song.html",song=song[0])


@app.route('/profile/<user_id>')
def profile(user_id):
    songs_uploaded = Song.query.filter_by(user=user_id).all()
    return render_template("profile.html",songs=songs_uploaded,user_id=user_id)


@app.route('/delete/<song_id>', methods=['GET'])
def delete(song_id):
    
    if request.method == "GET":
        song = Song.query.filter_by(id=song_id).first()

        if session["id"] is None or session["id"]!=song.user:
            return login()
        try:
            db.session.delete(song)
            db.session.commit()

            try:
                print(song.file_loc)
                os.remove(os.path.normpath(song.file_loc))
            
            except Exception as e:
                return jsonify({'message': f'Error deleting file: {e}'}), 500


        except Exception as e:
            return jsonify({'message': f'Error deleting file: {e}'}), 500

        return profile(session["id"])
        