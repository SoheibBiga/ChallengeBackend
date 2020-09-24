import requests, json, os, connexion, time
from flask import Flask, request
from spotify_auth import SpotifyAuth
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Album, Artist, get_timestamp

SPOTIFY_URL_NEW_RELEASES = "https://api.spotify.com/v1/browse/new-releases"

def new_releases():
    spotify = SpotifyAuth()
    token = spotify.getUserToken()

    if 'error' in token:
        print(token)
    else:
        offsetTab = [0]
        i = 0
        for offset in offsetTab:
            body = {
                "limit": 50,
                "offset": offset
            }

            headers = {
                "Content-Type": spotify.HEADER,
                "Authorization": f"Bearer {token['access_token']}",
            }

            get = requests.get(SPOTIFY_URL_NEW_RELEASES, params=body, headers=headers)
            data = json.loads(get.text)
            if 'error' in data:
                print(data)
            else:
                if (i+1)*50 != data["albums"]["total"]:
                    i+=1
                    offsetTab.append(i)
                try:
                    for album in data["albums"]["items"]:
                        album_data = Album(album["album_type"], album["available_markets"], album["external_urls"], album["href"], album["id"], album["name"], album["type"], album["uri"])

                        for artist in album["artists"]:
                            getMoreData = requests.get(artist["href"], params=body, headers=headers)
                            moreData = json.loads(getMoreData.text)
                            if 'error' in moreData:
                                artist_data = Artist(artist["external_urls"], artist["href"], artist["id"], artist["name"], artist["type"], artist["uri"])
                            else:
                                artist_data = Artist(artist["external_urls"], artist["href"], artist["id"], artist["name"], artist["type"], artist["uri"], moreData["followers"]["total"], moreData["popularity"], moreData["genres"])
                            album_data.artists.append(artist_data)

                        db.session.add(album_data)
                        db.session.commit()
                except(IntegrityError):
                    db.session.rollback()

scheduler = BackgroundScheduler()
job = scheduler.add_job(new_releases, 'interval', days=1)
scheduler.start()

@app.route('/api/artist', methods=['GET'])
def getArtists():
    today = get_timestamp()
    artists_data = Artist.query.filter(Artist.timestamp == today).all()
    results = [
        {
            "name": artist.name,
            "artist_id": artist.artist_id,
            "type": artist.type,
            "href": artist.href,
            "uri": artist.uri,
            "external_urls": artist.external_urls,
            "followers": artist.followers,
            "popularity": artist.popularity,
            "genres": artist.genres,
            "timestamp": artist.timestamp
        } for artist in artists_data
        ]
    return {"count": len(results), "artists": results}

if __name__ == '__main__':
    app.run()
