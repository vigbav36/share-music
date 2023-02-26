import os
from flask import Flask, jsonify, render_template, request, send_file, url_for, redirect, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate, migrate
import uuid
from sqlalchemy.sql import func


"""
Initial flask app configurations
"""

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

from models import Song,User

"""
Application Routing Logic
"""

@app.route('/song/<path:filename>')
def song(filename):
    """
    Fetch mp3 files from the songs directory
    """
    filename = os.path.basename(filename)
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/download/<path:filename>/<title>')
def download(filename,title):
    """
    Download mp3 files from the songs directory
    """
    filename = os.path.basename(filename)
    return send_from_directory(UPLOAD_FOLDER,filename,as_attachment=True,download_name=f'{title}.mp3')

@app.route('/')
def index():
    """
    Home page
    """
    songs = Song.query.all()
    return render_template('index.html',songs=songs,search=False)
    
@app.route('/login',methods=["POST","GET"])
def login():
    """
    User can login with their email id
    Exception handling for wrong credentials 
    """
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        user = User.query.filter_by(email=user_email).first()
        if user is None :
            return render_template("login.html",error="user does not exist");
        if(user.password == user_password):
            session['name'] = user.name
            session['id'] = user.id
            return redirect("/")
        else:
            return render_template("login.html",error="incorrect password")
    return render_template("login.html")

@app.route('/signup',methods=["POST","GET"])
def signup():
    """
    User can signup with their mail id and add other relevant bio data
    Exception handling for wrong credentials 
    """
    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        user_name = request.form.get("name")
        user_bio = request.form.get("bio")
        user_age = request.form.get("age")
        user = User.query.filter_by(email=user_email).all()
        if len(user) > 0:
            return render_template("signup.html",error="Account already exists with this mail id");
        try:
            id = str(uuid.uuid1().hex)
            user = User(
                id = id,
                email = user_email,
                password = user_password,
                name = user_name.lower(),
                bio = user_bio,
                age = int(user_age)
            )
            db.session.add(user)
            db.session.commit()

            return render_template("login.html")

        except Exception as e: 
            return render_template("signup.html",error=e)

    return render_template("signup.html")

@app.route("/logout")
def logout():
    """
    User can logout 
    """
    session["name"] = None
    return redirect("/")

def allowed_file(filename):
    """
    To check if a file is an mp3 file
    """
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload',methods=["POST","GET"])
def upload():
    """
    The songs are uploaded in the songs folder
    The id for the song is created using uuid library
    The file name is renamed to <song_id><.mp3> format
    The database is also updated
    """
    if request.method == "POST":
        
        if 'file' not in request.files:
            return render_template("upload.html",error="No file Selected")

        file = request.files['file']
        
        if file.filename == '':
            return render_template("upload.html",error="No File Selected")

        if file and allowed_file(file.filename):
            
            id = str(uuid.uuid1().hex)
            file_loc = os.path.join(UPLOAD_FOLDER, str(id)+".mp3")
            file.save(file_loc)
            try:
                song = Song(
                    id = id,
                    url = str("/play/"+str(id)),
                    title = str(request.form.get("title")).lower(),
                    artist = str(session["name"]).lower(),
                    user = str(session["id"]),
                    album= str(request.form.get("album")).lower(),
                    file_loc = str(file_loc)
                )
                db.session.add(song)
                db.session.commit()

            except Exception as e: 
                return render_template("upload.html",error=e)
            
            return index()
        else:
            return render_template("upload.html",error="Choose mp3 file")
    else:
        return render_template("upload.html")
        
@app.route("/search", methods=["POST","GET"])
def search():
    """
    Search query is used to match for songs, artists, and albums
    If there are no exact matches then we use a regular expression to find the closest matches
    The result is displayed seperately for songs, artists and albums
    """
    if request.method == "POST":

        search_query = request.form.get("search").lower()

        if search_query=="":
            return index()
       
        exact_match_title = Song.query.filter_by(title=search_query).all()
        exact_match_artist = User.query.filter_by(name=search_query).all()
        exact_match_album = Song.query.filter_by(album=search_query).all()

        if len(exact_match_title) == 0:
            close_match_title = Song.query.filter(Song.title.op('regexp')(rf'[.]*{search_query}[.]*')).all()
            songs_title=close_match_title

        else:
            songs_title=exact_match_title
        
        if len(exact_match_artist) == 0:
            close_match_artist = User.query.filter(User.name.op('regexp')(rf'[.]*{search_query}[.]*')).all()
            artists=close_match_artist
        else:
            artists=exact_match_artist

        if len(exact_match_album) == 0:
            close_match_album = Song.query.filter(Song.album.op('regexp')(rf'[.]{search_query}[.]*')).all()
            songs_album=close_match_album
        else:
            songs_album=exact_match_album

        return render_template("index.html",songs_title=songs_title,artists=artists,songs_album=songs_album,search=True)

@app.route('/play/<song_id>')
def play(song_id):
    """
    Songs are fetched by their custom url that includes its id
    Every song has a dedicated page to stream and download it
    """
    song = Song.query.filter_by(id=song_id).all()
    if len(song) == 0:
        return jsonify({'message': f':File has been deleted or removed'}), 500
    else:
        return render_template("song.html",song=song[0])


@app.route('/profile/<user_id>')
def profile(user_id):
    """
    Every user/artist is given a profile page
    It contains the songs and albums uploaded by the user
    """
    songs_uploaded = Song.query.filter_by(user=user_id).all()
    albums=set()
    for song in songs_uploaded:
        albums.add(song.album)

    return render_template("profile.html",songs=songs_uploaded,user_id=user_id,user_name=User.query.filter_by(id=user_id).first().name,albums=albums)


@app.route('/delete/<song_id>', methods=['GET'])
def delete(song_id):
    """
    Songs can be deleted from both the databse and the local storage in the songs directory
    """
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


@app.route('/album/<user_id>/<album>')
def album(user_id,album):
    """
    Album view page that has all the songs in that album
    """
    songs = Song.query.filter_by(user=user_id,album=album).all()
    return render_template("album.html",album=album,songs=songs)
    