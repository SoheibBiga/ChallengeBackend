from app import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d"))

new_releases = db.Table('new_releases',
    db.Column('album_id', db.String(), db.ForeignKey('albums.id'), primary_key=True),
    db.Column('artist_id', db.String(), db.ForeignKey('artists.id'), primary_key=True)
)

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.String(), primary_key=True)
    external_urls = db.Column(JSON)
    href = db.Column(db.String())
    name = db.Column(db.String())
    type = db.Column(db.String())
    uri = db.Column(db.String())
    followers = db.Column(db.Integer())
    popularity = db.Column(db.Integer())
    genres = db.Column(JSON)
    timestamp = db.Column(db.Date())

    def __init__(self, external_urls, href, artist_id, name, type, uri, followers=-1, popularity=-1, genres=["unknown"]):
        self.id = artist_id
        self.external_urls = external_urls
        self.href = href
        self.name = name
        self.type = type
        self.uri = uri
        self.followers = followers
        self.popularity = popularity
        self.genres = genres
        self.timestamp = get_timestamp()

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Album(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.String(), primary_key=True)
    album_type = db.Column(db.String())
    available_markets = db.Column(JSON)
    external_urls = db.Column(JSON)
    href = db.Column(db.String())
    name = db.Column(db.String())
    type = db.Column(db.String())
    uri = db.Column(db.String())
    artists = db.relationship("Artist", secondary=new_releases)

    def __init__(self, album_type, available_markets, external_urls, href, album_id, name, type, uri):
        self.id = album_id
        self.album_type = album_type
        self.available_markets = available_markets
        self.external_urls = external_urls
        self.href = href
        self.name = name
        self.type = type
        self.uri = uri

    def __repr__(self):
        return '<id {}>'.format(self.id)
