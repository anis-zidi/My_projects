#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
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
from flask_moment import Moment
from sqlalchemy import func, inspect
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from config import SQLALCHEMY_DATABASE_URI
from forms import ShowForm, VenueForm, ArtistForm
from flask_migrate import Migrate
from datetime import datetime
import sys
import traceback
from models import Venue, Show, Artist, app, db

#----------------------------------------------------------------------------#
# Filters.                                              #Edited#
#----------------------------------------------------------------------------#

# we added <locale='en'> ! this was found in a pinned question at my classroom!

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.                                          #NO_ACTION#
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues                                                 #DONE#
#----------------------------------------------------------------------------#
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  #First we will query all areas with distinct cities and states
  all_areas = Venue.query.distinct(Venue.city, Venue.state).all()
  
  #Second we will itirate throught all_areas to count number of upcoming shows with 2 conditions
  # start_time must be > to now's date and they have both the same id 
  # We will use .join to join Venue adn Show
  # We used <query-cheat-sheet> from the classroom for the coumentation of query.join and filter_by
  for a in all_areas:
    list1 = Venue.query.join(Show).filter(Show.start_time > datetime.now(), Show.Venue_id == a.id).all()
    num_shows = len(list1)
    all_venues = Venue.query.filter_by(city=a.city, state=a.state).all()
    for v in  all_venues:
      result={
        "city": a.city,
        "state": a.state,
        "venues":[{
          "id": v.id,
          "name": v.name,
          "num_upcoming_shows": num_shows
        }]
      }
      data.append(result)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  #filter_by is used for simple queries, filter is used for more powerful queries. #This definition is from stackoverflow.com
  # The documentation of <query.ilike> is from kb.objectrocket.com
  searched = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

  for v in searched:
    result= Venue.query.join(Show).filter(Show.start_time > datetime.now(), Show.Venue_id == v.id).all()
    response = {
      "count": len(searched),
      "data": [{
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(result)
      }]
    }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  upcoming_shows = []
  passed_shows = []
  quered_venue = Venue.query.filter_by(id=venue_id).first()
  all_shows = Show.query.filter_by(
    Venue_id = quered_venue.id
  ).all()

  for sh in all_shows:
    start_time = format_datetime(str(sh.start_time))
    artist = Artist.query.filter_by(id=Show.Artist_id).first()
    if sh.start_time >= datetime.now():
      upcoming_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": start_time
      })
    else: 
      passed_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": start_time
      })

    data = {
      "id": quered_venue.id,
      "name": quered_venue.name,
      "genres": quered_venue.genres,
      "address": quered_venue.address,
      "city": quered_venue.city,
      "state": quered_venue.state,
      "phone": quered_venue.phone,
      "website": quered_venue.website,
      "facebook_link": quered_venue.facebook_link,
      "image_link": quered_venue.image_link,
      "seeking_talent": quered_venue.seeking_talent,
      "seeking_description": quered_venue.seeking_description,
      "past_shows": passed_shows,
      "past_shows_count": len(passed_shows),
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows)
    }
  
  
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  
  return render_template('pages/show_venue.html', venue=data)

#----------------------------------------------------------------------------#
#  Create Venue                                            #DONE#  EDITED
#----------------------------------------------------------------------------#
# We will be using the method of getting user data from the view (in Flask) LESSON-5
# User input is : Form input
# request.data Contains the incoming request data as string in case it came with a mimetype Flask does not handle. #This is a definition from stackoverflow.com

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    website = request.form['website']

    add_venue = Venue (name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, website=website, image_link=image_link)
    form.populate_obj(add_venue)

    db.session.add(add_venue)
    db.session.commit()  
  
    flash('Venue ' + add_venue.name + ' was successefully listed')
  except ValueError as e:
    print(e)
    db.session.rollback()
    traceback.print_exc()
    flash('An error occured! Venue ' + add_venue.name + ' could not be listed')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  # We used query-cheat-sheet from our courses to queyr and filter data by venue_id.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#----------------------------------------------------------------------------#
#  Artists                                                #DONE#
#----------------------------------------------------------------------------#

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # We are not asked to group artist by state and cities !

  data=[]
  for ar in Artist.query.all():
    data.append({
      "id": ar.id,
      "name": ar.name
    })
  
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #We will use the same princip as in venues to search for artists
  #We will be using .join() .ilike()
  search_term = request.form['search_term']
  searched = Artist.query.filter(Artist.name.ilike('%' + search_term  +'%')).all()

  for a in searched:
    result = Artist.query.join(Show).filter(Show.start_time > datetime.now(), Show.Artist_id == a.id).all()
    response = {
      "count": len(searched),
      "data": [{
        "id" : a.id,
        "name": a.name,
        "num_upcoming_shows": len(result)
      }]
    }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # TODO: replace with real venue data from the venues table, using venue_id
  # we will use the same method in showing data as Venues
  data = []
  upcoming_shows = []
  passed_shows = []
  #We created two listes in wich we will insert the upcoming and passed shows based on datetime.now()
  quered_artist = Artist.query.filter_by(id=artist_id).first()
  all_shows = Show.query.filter_by(
    Artist_id = quered_artist.id
  ).all()

  for sh in all_shows:
    start_time = format_datetime(str(sh.start_time))
    venue = Venue.query.filter_by(id=Show.Venue_id).first()
    if sh.start_time >= datetime.now():
      upcoming_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": start_time
      })
    else:
      passed_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": start_time
      })
    
    data = {
      "id": quered_artist.id,
      "name": quered_artist.name,
      "genres": quered_artist.genres,
      "city": quered_artist.city,
      "state": quered_artist.state,
      "phone": quered_artist.phone,
      "website": quered_artist.website,
      "facebook_link": quered_artist.facebook_link,
      "image_link": quered_artist.image_link,
      "seeking_talent": quered_artist.seeking_talent,
      "seekin_venue": quered_artist.seeking_venue,
      "past_shows": passed_shows,
      "past_shows_count": len(passed_shows),
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows)
    }
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  return render_template('pages/show_artist.html', artist=data)

#----------------------------------------------------------------------------#
#  Update                                                 #DONE#
#----------------------------------------------------------------------------#
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  #update
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.genres.data = artist.genres
  form.website.data = artist.website
  form.seeking_talent.data = artist.seeking_talent
  form.seeking_venue.data = artist.seeking_venue

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Venue.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.genres = request.form['genres']
    artist.website = request.form['website']
    artist.seeking_talent = request.form['seeking_talent']
    artist.seeking_venue = request.form['seeking_venue']
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.facebook_link.data = venue.facebook_link
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name'],
    venue.city = request.form['city'],
    venue.state = request.form['state'],
    venue.address = request.form['address'],
    venue.phone = request.form['phone'],
    venue.genres = request.form.getlist('genres'),
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = request.form['seeking_talent']
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#----------------------------------------------------------------------------#
#  Create Artist                                          #DONE#
#----------------------------------------------------------------------------#
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  # Same as we did with adding a new venue.
  form = ArtistForm(request.form)
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres')
    website = request.form['website']
    image_link = request.form['image_link']

    add_artist = Artist (name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, website=website, image_link=image_link)
    form.populate_obj(add_artist)

    db.session.add(add_artist)
    db.session.commit()
    flash('Artist ' + add_artist.name + ' was successfully listed!') 
  except ValueError as e:
    print(e)
      # TODO DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred due to database insertion error. Artist ' + add_artist.name + ' could not be listed.')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Shows                                                  #DONE#
#----------------------------------------------------------------------------#
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_shows = Show.query.all()
  data = []
  # First we will itirate throught all the shows to find artist and venue with the id listed in Show.
  # Then we will take the correct artist and venue
  #finally we will use the same form to append values in data.
  # we made the start time an str form to resolve this error :
  #<TypeError: Parser must be a string or character stream, not datetime>
  for i in all_shows:
    ar = Artist.query.filter_by(id = i.Artist_id).first()
    vn = Venue.query.filter_by(id = i.Venue_id).first()
    data.append({
            "Venue_id": vn.id,
            "venue_name": vn.name,
            "artist_id": ar.id,
            "artist_name": ar.name,
            "artist_image_link": ar.image_link,
            "start_time": str(i.start_time)
    })
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # Since Show is an association table we use the methode : insert() to add inputs. 
  # Instead of using session.add() we'll be using session.execute().

  try:
    Venue_id = request.form['venue_id']
    Artist_id = request.form['artist_id']
    start_time = request.form['start_time']
      
    add_show = Show (Venue_id=Venue_id, Artist_id=Artist_id, start_time = start_time)

    db.session.add(add_show)
    db.session.commit()
    flash('Show was successfully listed!') 
  except: 
      flash('An error occurred due to database insertion error.')
      traceback.print_exc()
  finally:
      db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.                                                 #NO_ACTION#
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
