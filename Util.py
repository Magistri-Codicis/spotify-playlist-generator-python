import os
import random

import spotipy
from spotipy import SpotifyOAuth


def load_env():
    with open('.env') as f:
        for line in f:
            key, value = line.split('=')
            os.environ[key] = value.rstrip()


class Util:

    def __init__(self):
        self.sp = None
        self.username = None
        self.playlist_id = None
        load_env()
        self.authenticate()

    def authenticate(self):
        scope = 'playlist-modify-public'
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        self.username = self.sp.me()['display_name']

    def search_artists(self, artist_list):
        result = []
        for search_artist in artist_list:
            result.append(self.sp.search(q='artist:' + search_artist, type='artist', limit=5))
        return result

    def create_playlist(self, playlist_name):
        self.sp.user_playlist_create(self.username, playlist_name)
        self.playlist_id = self.sp.user_playlists(self.username)['items'][0]['id']

    def get_top_tracks(self, artist_id, count=5):
        tracks = []
        result = self.sp.artist_top_tracks(artist_id, country="CH")
        for track in result['tracks'][:count]:
            tracks.append(track['id'])
        return tracks

    def add_tracks(self, tracks):
        self.sp.playlist_add_items(self.playlist_id, [tracks])

    def get_all_tracks(self, selected_artists, tracks_per_artist=5, shuffle=False):
        tracks = []
        for artist, artist_id in selected_artists.items():
            tracks.append(self.get_top_tracks(artist_id, tracks_per_artist))
        if shuffle:
            random.shuffle(tracks)
        return tracks
