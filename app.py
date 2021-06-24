# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, config
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

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
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

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
    data = []
    venues_s = Venue.query.all()
    cities_and_states = []
    for venue in venues_s:
        cities_and_states.append({'city': venue.city, 'state': venue.state})

    this_time = datetime.now()

    for loc in cities_and_states:
        ven_list = []
        for venue in venues_s:
            if venue.city == loc["city"] and venue.state == loc["state"]:
                ven_shows = Show.query.filter_by(venue_id=venue.id).all()
                upcoming = 0
                for show in ven_shows:
                    if show.start_time > this_time:
                        upcoming += 1

                ven_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "upcoming_shows": upcoming
                })
        data.append({
            "city": loc["city"],
            "state": loc["state"],
            "venues": ven_list
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search = request.form.get('search_term', '')
    search_result = Venue.query.filter(Venue.name.ilike(f'%{search}%'))
    response = {
        "count": search_result.count(),
        "data": search_result
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venues_all = Venue.query.filter_by(id=venue_id).first()
    shows_all = Show.query.filter_by(venue_id=venue_id).all()
    this_time = datetime.now()
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows = []
    past_shows_count = 0
    for show in shows_all:
        show_the_artist = Artist.query.filter_by(id=show.artist_id).first()
        if show.start_time > this_time:
            upcoming_shows.append({
                "artist_id": show_the_artist.id,
                "artist_name": show_the_artist.name,
                "artist_image_link": show_the_artist.image_link,
                "start_time": str(show.start_time)
            })
            upcoming_shows_count += 1
        else:
            past_shows.append({
                "artist_id": show_the_artist.id,
                "artist_name": show_the_artist.name,
                "artist_image_link": show_the_artist.image_link,
                "start_time": str(show.start_time)
            })
            past_shows_count += 1

    data = {
        "id": venues_all.id,
        "name": venues_all.name,
        "genres": [venues_all.genres],
        "address": venues_all.address,
        "city": venues_all.city,
        "state": venues_all.state,
        "phone": venues_all.phone,
        "website": venues_all.website,
        "facebook_link": venues_all.facebook_link,
        "seeking_talent": venues_all.seeking_talent,
        "seeking_description": venues_all.seeking_description,
        "image_link": venues_all.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = VenueForm()
        add_venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            genres=form.genres.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )

        db.session.add(add_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.' + str(e))
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue_del = Venue.query.filter(Venue.id == venue_id).first()
        name_del = venue_del.name
        db.session.delete(venue_del)
        db.session.commit()
        flash('Venue ' + name_del + ' was deleted successfully.')
    except:
        db.session.rollback()
        flash('Venue ' + name_del + ' could not be deleted.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search = request.form.get('search_term', '')
    search_result = Artist.query.filter(Artist.name.ilike(f'%{search}%'))
    response = {
        "count": search_result.count(),
        "data": search_result
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_all = Artist.query.filter_by(id=artist_id).first()
    shows_all = Show.query.filter_by(artist_id=artist_id).all()
    this_time = datetime.now()
    upcoming_shows = []
    upcoming_shows_count = 0
    past_shows = []
    past_shows_count = 0
    for show in shows_all:
        show_the_venue = Venue.query.filter_by(id=show.venue_id).first()
        if show.start_time > this_time:
            upcoming_shows.append({
                "venue_id": show_the_venue.id,
                "venue_name": show_the_venue.name,
                "venue_image_link": show_the_venue.image_link,
                "start_time": str(show.start_time)
            })
            upcoming_shows_count += 1
        else:
            past_shows.append({
                "venue_id": show_the_venue.id,
                "venue_name": show_the_venue.name,
                "venue_image_link": show_the_venue.image_link,
                "start_time": str(show.start_time)
            })
            past_shows_count += 1

    data = {
        "id": artist_all.id,
        "name": artist_all.name,
        "genres": [artist_all.genres],
        "city": artist_all.city,
        "state": artist_all.state,
        "phone": artist_all.phone,
        "website": artist_all.website,
        "facebook_link": artist_all.facebook_link,
        "seeking_venue": artist_all.seeking_venue,
        "seeking_description": artist_all.seeking_description,
        "image_link": artist_all.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    get_artist = Artist.query.filter_by(id=artist_id).first()
    artist = {
        "id": get_artist.id,
        "name": get_artist.name,
        "genres": get_artist.genres,
        "city": get_artist.city,
        "state": get_artist.state,
        "phone": get_artist.phone,
        "website": get_artist.website,
        "facebook_link": get_artist.facebook_link,
        "seeking_venue": get_artist.seeking_venue,
        "seeking_description": get_artist.seeking_description,
        "image_link": get_artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()
        artist_edit = Artist.query.get(artist_id)
        name = form.name.data
        artist_edit.name = name
        artist_edit.city = form.city.data
        artist_edit.state = form.state.data
        artist_edit.phone = form.phone.data
        artist_edit.image_link = form.image_link.data
        artist_edit.facebook_link = form.facebook_link.data

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' successfully updated')
    except:
        db.session.rollback()
        flash('Artist ' + name + ' could not been updated')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    get_venue = Venue.query.filter_by(id=venue_id).first()
    venue = {
        "id": get_venue.id,
        "name": get_venue.name,
        "genres": get_venue.genres,
        "address": get_venue.address,
        "city": get_venue.city,
        "state": get_venue.state,
        "phone": get_venue.phone,
        "website": get_venue.website,
        "facebook_link": get_venue.facebook_link,
        "seeking_talent": get_venue.seeking_talent,
        "seeking_description": get_venue.seeking_description,
        "image_link": get_venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        venue_edit = Venue.query.get(venue_id)
        name = form.name.data
        venue_edit.name = name
        venue_edit.city = form.city.data
        venue_edit.state = form.state.data
        venue_edit.address = form.address.data
        venue_edit.phone = form.phone.data
        venue_edit.image_link = form.image_link.data
        venue_edit.facebook_link = form.facebook_link.data
        venue_edit.website = form.website_link.data
        venue_edit.seeking_talent = form.seeking_talent.data
        venue_edit.seeking_description = form.seeking_description.data

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' successfully updated')
    except:
        db.session.rollback()
        flash('Venue ' + name + ' could not been updated')
    finally:
        db.session.close()

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
        form = ArtistForm()
        add_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(add_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist_del = Artist.query.filter(Artist.id == artist_id).first()
        name_del = artist_del.name
        db.session.delete(artist_del)
        db.session.commit()

        flash('Venue ' + name_del + ' was deleted successfully.')
    except:
        db.session.rollback()
        flash('Venue ' + name_del + ' could not be deleted.')
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
        venue_query = Venue.query.filter_by(id=show.venue_id).first()
        artist_query = Artist.query.filter_by(id=show.artist_id).first()
        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue_query.name,
            "artist_id": show.artist_id,
            "artist_name": artist_query.name,
            "artist_image_link": artist_query.image_link,
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
        form = ShowForm()
        show = Show(
            start_time=form.start_time.data,
            venue_id=form.venue_id.data,
            artist_id=form.artist_id.data,
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
