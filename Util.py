import os
import random

import spotipy
from spotipy import SpotifyOAuth


def load_env():
    with open('.env') as f:
        for line in f:
            key, value = line.split('=')
            os.environ[key] = value.rstrip()


def flattenArray(array):
    for sublist in array:
        for item in sublist:
            yield item
    return array


class Util:

    def __init__(self):
        self.sp = None
        self.username = None
        self.playlist_id = None
        load_env()

    def authenticate(self):
        scope = 'playlist-modify-public'
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        self.username = self.sp.me()['display_name']

    def search_artists(self, artist_list):
        result = []
        for search_artist in artist_list:
            result.append(self.search_artist(search_artist))
        return result

    def search_artist(self, query, limit=3):
        return self.sp.search(q='artist:' + query, type='artist', limit=limit)

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
        print(tracks)
        self.sp.playlist_add_items(self.playlist_id, tracks)

    def get_all_tracks(self, selected_artists, tracks_per_artist=5, shuffle=False):
        tracks = []
        for artist, artist_id in selected_artists.items():
            tracks.extend(self.get_top_tracks(artist_id, tracks_per_artist))
        if shuffle:
            random.shuffle(tracks)
        return tracks
