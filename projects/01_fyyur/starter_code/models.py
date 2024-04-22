from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import SQLALCHEMY_DATABASE_URI

# ---------------------------------------------------------------------------- #
# App Config.
# ---------------------------------------------------------------------------- #

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
with app.app_context():
    db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------------------------------------------------------------------------- #
# Models.
# ---------------------------------------------------------------------------- #


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    address = db.Column(db.String(250))
    phone = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(250))
    genres = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    website_link = db.Column(db.String(250), nullable=True)
    shows = db.relationship("Show", backref="venue", lazy=True)

    def __str__(self):
        return f'Venue has {self.id} and named {self.name}'

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    phone = db.Column(db.String(250))
    genres = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(250))
    website_link = db.Column(db.String(250))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(250), nullable=True)

    shows = db.relationship("Show", backref="artist", lazy=True)

    def __str__(self):
        return f'Artist has {self.id} and named {self.name}'

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey(Artist.id),
        nullable=False
    )
    venue_id = db.Column(
        db.Integer,
        db.ForeignKey(Venue.id),
        nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=False)
