
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify
)
from config import SQLALCHEMY_DATABASE_URI
from forms import ShowForm, VenueForm, ArtistForm

#----------------------------------------------------------------------------#
# App Config.                                            #DONE#
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.                                                 #DONE#
#----------------------------------------------------------------------------#
# We will use what we learned in lesson-7 to map tables using foreign keys!

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(400)) 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
   
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
      return 'Venue ID: {self.id}, name: {self.name}'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_venue = db.Column(db.String(400)) 
    
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
      return 'Artist ID:{self.id}, name: {self.name}'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  Venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  Artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime)

  def __repr__(self):
    return 'Show ID: {self.id}, Venue ID: {self.Venue_id}, Artist ID: {self.Artist_id}'
