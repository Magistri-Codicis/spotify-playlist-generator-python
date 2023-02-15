import os
import random
from typing import List

import requests.exceptions
import spotipy
import urllib3.exceptions
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QMessageBox, QWidget, QTextEdit
from spotipy import SpotifyOAuth

from Artist.ArtistListEntry import ArtistListEntry


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


def log_to_widget(text, output_widget: QTextEdit):
    if output_widget is not None:
        output_widget.append(text)
    else:
        print(text)


class Util(QThread):
    output = pyqtSignal(int, str, int)
    progress = 0

    # TODO: Refactor to use signals
    def __init__(self):
        super(Util, self).__init__()
        self.shuffle = None
        self.playlist_description = None
        self.playlist_name = None
        self.tracks_per_artist = None
        self.artists = None
        self.isGenerating = False
        self.sp: spotipy.Spotify = None
        self.username = None
        self.playlist_id = None
        self.output_widget = None
        load_env()

    def run(self):
        self.generate(self.artists, self.tracks_per_artist, self.playlist_name, self.playlist_description,
                      self.shuffle)

    def __del__(self):
        self.exiting = True
        self.wait()

    def authenticate(self):
        try:
            scope = 'playlist-modify-public'
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
            self.username = self.sp.me()['display_name']
            self.output.emit(0, 'Successfully authenticated as ' + self.username, 100)
        except requests.exceptions.ConnectionError or urllib3.exceptions.MaxRetryError:
            QMessageBox.about(QWidget(), "Network Error", "No Connection established. Check you Internet connection.")

    def search_artists(self, artist_list):
        result = []
        for search_artist in artist_list:
            result.append(self.search_artist(search_artist))
        return result

    def search_artist(self, query, limit=3):
        return self.sp.search(q='artist:' + query, type='artist', limit=limit)

    def create_playlist(self, playlist_name, playlist_description=""):
        self.output.emit(0, "Creating Playlist...", self.progress)
        self.sp.user_playlist_create(self.username, playlist_name, description=playlist_description)
        self.playlist_id = self.sp.user_playlists(self.username)['items'][0]['id']
        self.progress += 10

    def get_filler_tracks(self, artist_id, current_list: dict = dict, limit=5, offset=0, country='CH'):
        raw_tracks = []
        tracks = dict()
        request_limit = limit + offset
        if request_limit <= 50:
            result = self.sp.artist_albums(artist_id, limit=request_limit, country=country,
                                           album_type='album,single')
        else:
            result = self.sp.artist_albums(artist_id, limit=50, country=country, album_type='album,single')
            loop_count = int(request_limit / 50)
            while len(result) < request_limit and loop_count > 0:
                new_tracks = self.sp.artist_albums(artist_id, limit=50, offset=len(result), country=country,
                                                   album_type='album,single')['items']
                if len(new_tracks) == 0:
                    break
                result['items'].extend(new_tracks)
                loop_count -= 1

        for album in result['items']:
            album_tracks = []
            for track in self.sp.album_tracks(album['id'])['items']:
                album_tracks.append(track['id'])
            track_catalog = self.sp.tracks(album_tracks)
            raw_tracks.extend(track_catalog['tracks'])

        raw_tracks.sort(key=lambda x: x['popularity'], reverse=True)
        loop_count = 0
        loop_limit = limit * 2
        for track in raw_tracks[offset:]:
            compare_tracks = tracks | current_list
            if track['id'] not in compare_tracks.keys() and any(
                    artist['id'] == artist_id for artist in track['artists']) and \
                    not any(compare_tracks[comp_track]['name'] == track['name'] for comp_track in compare_tracks):
                tracks[track['id']] = {'name': track['name'], 'artist': track['artists'][0]['id']}
            if len(tracks) == limit or loop_count >= loop_limit:
                break
            loop_count += 1
        if len(tracks) < limit:
            tracks.update(self.get_filler_tracks(artist_id, current_list | tracks, limit - len(tracks),
                                                 offset + len(raw_tracks), country))
        return tracks

    def add_tracks(self, tracks):
        self.output.emit(0, "Adding Tracks...", self.progress)
        if len(tracks) > 100:
            for i in range(0, len(tracks), 100):
                self.progress += 10 / len(tracks)
                self.sp.playlist_add_items(self.playlist_id, tracks[i:i + 100])
                self.output.emit(0, "Adding Tracks...", self.progress)
        else:
            self.sp.playlist_add_items(self.playlist_id, tracks)
            self.progress += 10

    def get_all_tracks(self, selected_artists: List[ArtistListEntry], tracks_per_artist=5, shuffle=False):
        self.progress += 10
        self.output.emit(0, "Searching for tracks...", self.progress)
        tracks = dict()
        return_tracks = []
        for artist_entry in selected_artists:
            self.output.emit(0,
                             "Searching for tracks by " + artist_entry.result_list[artist_entry.selected_artist].name,
                             self.progress)
            search_tracks = self.get_filler_tracks(artist_entry.result_list[artist_entry.selected_artist].artist_id,
                                                   limit=tracks_per_artist, current_list=tracks)
            tracks.update(search_tracks)
            self.progress += int(60 / len(selected_artists))
        return_tracks.extend(tracks.keys())
        if shuffle:
            self.output.emit(0, "Shuffling tracks...", self.progress)
            random.shuffle(return_tracks)
        return return_tracks

    def generate_playlist(self, artists, tracks_per_artist, playlist_name, playlist_description, shuffle,
                          output_widget: QTextEdit = None):
        self.artists = artists
        self.tracks_per_artist = tracks_per_artist
        self.playlist_name = playlist_name
        self.playlist_description = playlist_description
        self.shuffle = shuffle
        self.output_widget = output_widget
        self.start()

    def generate(self, artists, tracks_per_artist, playlist_name, playlist_description, shuffle):
        self.progress = 0
        self.output.emit(0, "Starting to generate....", self.progress)
        self.output.emit(0, "Configuration", self.progress)
        self.output.emit(0, "Tracks per artist: " + str(tracks_per_artist), self.progress)
        self.output.emit(0, "Playlist name: " + playlist_name, self.progress)
        self.output.emit(0, "Playlist description: " + playlist_description, self.progress)
        self.output.emit(0, "Shuffle: " + str(shuffle), self.progress)
        self.output.emit(0, "--------------------------", self.progress)
        tracks = self.get_all_tracks(artists, tracks_per_artist, shuffle)
        self.output.emit(0, "Found " + str(len(tracks)) + " tracks", self.progress)
        self.create_playlist(playlist_name, playlist_description)
        self.output.emit(0, "Created playlist", self.progress)
        self.add_tracks(tracks)
        self.output.emit(0, "Added tracks", self.progress)
        self.progress = 100
        self.output.emit(1, "Finished", self.progress)
        self.output.emit(3, f"Playlist at: https://open.spotify.com/playlist/{self.playlist_id}", self.progress)
