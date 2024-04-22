# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from config import SQLALCHEMY_DATABASE_URI
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from models import Artist, Show, Venue, db
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db.init_app(app)
with app.app_context():
    db.create_all()
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venue_list = Venue.query.all()
    city_list = []
    response = []

    for venue in venue_list:
        if venue.city not in city_list:
            city_list.append(venue.city)
            response.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "num_upcoming_shows": len(item.shows)
                    }
                    for item in venue_list
                    if item.city == venue.city
                ]
            })
    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    terms = search_term.strip().split(',')
    response = {"count": 0, "data": []}

    if len(terms) == 2:
        city, state = terms
        city = city.strip()
        state = state.strip()
        venues = Venue.query.filter(
            Venue.city.ilike(f'%{city}%'),
            Venue.state.ilike(f'%{state}%'))
    else:
        venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    response["count"] = venues.count()
    for venue in venues:
        response["data"].append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(venue.shows)
        })
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    response = {
        "id": venue.id,
        "name": venue.name,
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "image_link": venue.image_link,
        "facebook_link": venue.facebook_link,
        "genres": venue.genres,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "website_link": venue.website_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = VenueForm(request.form)
        name = form.name.data.strip()
        city = form.city.data.strip()
        state = form.state.data.strip()
        address = form.address.data.strip()
        phone = form.phone.data.strip()
        image_link = form.image_link.data.strip()
        facebook_link = form.facebook_link.data.strip()
        genres = ",".join(form.genres.data)
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data.strip()
        website = form.website_link.data.strip()

        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            genres=genres,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description,
            website_link=website
        )

        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception:
        db.session.rollback()
        flash(
            'An error occurred. Venue '
            + request.form['name']
            + ' could not be listed.'
        )
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        for show in venue.shows:
            db.session.delete(show)
        db.session.delete(venue)
        db.session.commit()
        flash(venue.name + ' was successfully deleted!')
    except Exception:
        db.session.rollback()
        flash(
            'An error occurred. Venue '
            + venue.name
            + ' could not be deleted!!!'
        )
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    terms = search_term.strip().split(',')

    response = {"count": 0, "data": []}

    if len(terms) == 2:
        city, state = terms
        city = city.strip()
        state = state.strip()
        artists = Artist.query.filter(
            Artist.city.ilike(f'%{city}%'),
            Artist.state.ilike(f'%{state}%')
        )
    else:
        artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    response["count"] = artists.count()
    for artist in artists:
        response["data"].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist.shows)
        })
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    past_shows = []
    past_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    for show in past_shows_query:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows = []
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "genres": artist.genres,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "website": artist.website_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.default = artist.name
    form.city.default = artist.city
    form.state.default = artist.state
    form.phone.default = artist.phone
    form.genres.default = artist.genres.split(",")
    form.image_link.default = artist.image_link
    form.facebook_link.default = artist.facebook_link
    form.website_link.default = artist.website_link
    form.seeking_venue.default = artist.seeking_venue
    form.seeking_description.default = artist.seeking_description

    form.process()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm(request.form)
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = ",".join(form.genres.data)
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Artist '
              + request.form['name']
              + ' could not be updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.default = venue.name
    form.city.default = venue.city
    form.state.default = venue.state
    form.address.default = venue.address
    form.phone.default = venue.phone
    form.image_link.default = venue.image_link
    form.facebook_link.default = venue.facebook_link
    form.genres.default = venue.genres.split(",")
    form.seeking_talent.default = venue.seeking_talent
    form.seeking_description.default = venue.seeking_description
    form.website_link.default = venue.website_link

    form.process()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm(request.form)
        venue = Venue.query.get(venue_id)

        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.genres = ",".join(form.genres.data)
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.website = form.website_link.data

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Venue '
              + request.form['name']
              + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm(request.form)

        name = form.name.data.strip()
        city = form.city.data.strip()
        state = form.state.data.strip()
        phone = form.phone.data.strip()
        genres = ",".join(form.genres.data)
        image_link = form.image_link.data.strip()
        facebook_link = form.facebook_link.data.strip()
        website = form.website_link.data.strip()
        seeking_venue = form.seeking_venue.data
        seeking_description = form.seeking_description.data.strip()

        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website_link=website,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form["name"] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []

    shows = Show.query.all()
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form = ShowForm(request.form)

        artist_id = int(form.artist_id.data)
        venue_id = int(form.venue_id.data)
        start_time = form.start_time.data

        show = Show(
            artist_id=artist_id,
            venue_id=venue_id,
            start_time=start_time
        )

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
