from app import db

"""
Models for the database
"""

class User(db.Model):
    """
    User table that stores user's information
    """
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(80), unique=True, nullable=False)
    bio = db.Column(db.Text)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.name} email {self.email}>'

class Song(db.Model):
    """
    Song table that stores information related to a song uploaded
    """
    id = db.Column(db.String(500), primary_key=True)
    url = db.Column(db.String(500),unique=True ,nullable=False)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    file_loc = db.Column(db.String(600), nullable=False)

    def __repr__(self):
        return f'<Song {self.title} artist {self.artist}>'