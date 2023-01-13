import os
import random
from typing import List

import requests.exceptions
import spotipy
import urllib3.exceptions
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


class Util:

    def __init__(self):
        self.sp: spotipy.Spotify = None
        self.username = None
        self.playlist_id = None
        load_env()

    def authenticate(self):
        try:
            scope = 'playlist-modify-public'
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
            self.username = self.sp.me()['display_name']
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
        self.sp.user_playlist_create(self.username, playlist_name, description=playlist_description)
        self.playlist_id = self.sp.user_playlists(self.username)['items'][0]['id']

    def get_top_tracks(self, artist_id, count=5, offset=0, country='CH'):
        tracks = []
        result = self.sp.artist_top_tracks(artist_id, country=country)
        for track in result['tracks'][:count]:
            tracks.append(track['id'])
        return tracks

    def get_filler_tracks(self, artist_id, current_list=[], limit=5, offset=0, country='CH'):
        raw_tracks = []
        tracks = []
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
        print("Raw Tracks: " + str(len(raw_tracks)))
        loop_count = 0
        loop_limit = limit * 2
        for track in raw_tracks[offset:]:
            if track['id'] not in current_list:
                tracks.append(track['id'])
            if len(tracks) == limit or loop_count >= loop_limit:
                break
            loop_count += 1
        return tracks

    def add_tracks(self, tracks):
        print(tracks)
        self.sp.playlist_add_items(self.playlist_id, tracks)

    def replace_duplicates(self, artist: ArtistListEntry, tracks_per_artist, search_tracks, existing_tracks, offset=0):
        intersection = set(search_tracks) & set(existing_tracks)
        if len(intersection) > 0:
            for i in intersection:
                search_tracks.remove(i)
            new_tracks = self.get_filler_tracks(artist.result_list[artist.selected_artist].artist_id,
                                                existing_tracks + search_tracks,
                                                limit=tracks_per_artist - len(search_tracks),
                                                offset=offset + tracks_per_artist)
            print("New tracks: " + str(len(new_tracks)))
            search_tracks.extend(new_tracks)

    def get_all_tracks(self, selected_artists: List[ArtistListEntry], tracks_per_artist=5, shuffle=False):
        tracks = []
        for artist_entry in selected_artists:
            search_tracks = self.get_filler_tracks(artist_entry.result_list[artist_entry.selected_artist].artist_id,
                                                   limit=tracks_per_artist, current_list=tracks)
            print("Artist: " + artist_entry.result_list[artist_entry.selected_artist].name)
            print("Before: " + str(len(search_tracks)))
            self.replace_duplicates(artist_entry, tracks_per_artist, search_tracks, tracks)
            print("After :" + str(len(search_tracks)))
            tracks.extend(search_tracks)
        if shuffle:
            random.shuffle(tracks)
        return tracks

    def generate_playlist(self, artists, tracks_per_artist, playlist_name, playlist_description, shuffle,
                          output_widget: QTextEdit = None):
        log_to_widget("Configuration", output_widget)
        log_to_widget("Tracks per artist: " + str(tracks_per_artist), output_widget)
        log_to_widget("Playlist name: " + playlist_name, output_widget)
        log_to_widget("Playlist description: " + playlist_description, output_widget)
        log_to_widget("Shuffle: " + str(shuffle), output_widget)
        log_to_widget("--------------------------", output_widget)
        log_to_widget("Searching for tracks.....", output_widget)
        tracks = self.get_all_tracks(artists, tracks_per_artist, shuffle)
        log_to_widget("Found " + str(len(tracks)) + " tracks", output_widget)
        log_to_widget("Creating playlist.....", output_widget)
        self.create_playlist(playlist_name, playlist_description)
        log_to_widget("Adding tracks to playlist.....", output_widget)
        self.add_tracks(tracks)
        log_to_widget("Done", output_widget)
        log_to_widget("--------------------------", output_widget)
        log_to_widget("Playlist created: " + f"https://open.spotify.com/playlist/{self.playlist_id}", output_widget)
        return f"https://open.spotify.com/playlist/{self.playlist_id}"
