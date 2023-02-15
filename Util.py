import os
import random
import requests
from typing import List

import requests.exceptions
import spotipy
import urllib3.exceptions
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QMessageBox, QWidget, QTextEdit
from spotipy import SpotifyOAuth

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager, EdgeChromiumDriverManager

from Artist.ArtistListEntry import ArtistListEntry

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


def get_selenium_driver():
    try:
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        return driver
    except:
        try:
            service = Service(executable_path=GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service)
            return driver
        except:
            try:
                service = Service(executable_path=EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service)
                return driver
            except:
                return None


def create_spotify_application(name, description, redirect_uris):
    url = "https://accounts.spotify.com/authorize?client_id=a5429cc04d0b4bf78872d22a60ec4c4b&response_type=token" \
          "&redirect_uri=https://developer.spotify.com/dashboard/oauth_callback/&scope=user-self-provisioning"

    # 1. Create a new instance of the Chrome driver
    driver = get_selenium_driver()

    if driver is None:
        print("Please install a supported browser like Chrome, Firefox or Edge")
        exit(0)

    # 2. Load the authentication URL and wait for the user to log in
    driver.follow_redirects = False
    driver.get(url)

    # 3. Wait for the user to be redirected to the callback URL and extract the access token
    WebDriverWait(driver, 9999).until(EC.url_contains("https://developer.spotify.com/dashboard"
                                                      "/oauth_callback"))

    redirect_url = driver.current_url
    access_token = redirect_url.split("access_token=")[1].split("&")[0]

    driver.quit()

    # Make the API call to create the Spotify application
    headers = {
        'authority': 'api.spotify.com',
        'accept': 'application/json',
        'authorization': f'Bearer {access_token}',
        'content-type': 'application/json',
    }
    data = {
        "name": name,
        "description": description,
        "homepage": "",
        "redirect_uris": redirect_uris
    }

    response = requests.post('https://api.spotify.com/webapi-provisioning/applications', headers=headers, json=data)

    if response.status_code == 200:
        print("Application created successfully")
        client_id = response.json()['client_id']
        client_secret = response.json()['client_secret']
    else:
        print(f"Request failed with error {response.status_code}")
        return

    return client_id, client_secret, redirect_uris[0]


def load_env():
    print("Loading .env file")
    if os.path.isfile('.env'):
        with open('.env', 'r') as f:
            for line in f:
                key, value = line.split('=')
                os.environ[key] = value.rstrip()
            f.close()
    else:
        print("No .env file found.")
        print("Creating new application")
        client_id, client_secret, redirect_uri = create_spotify_application("Playlist Generator",
                                                                            "Generates playlists from artists",
                                                                            ["http://localhost:9999/callback"])
        with open('.env', 'w') as f:
            f.write(f"SPOTIPY_CLIENT_ID={client_id}\n")
            f.write(f"SPOTIPY_CLIENT_SECRET={client_secret}\n")
            f.write(f"SPOTIPY_REDIRECT_URI={redirect_uri}\n")
            f.close()
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        os.environ['SPOTIPY_REDIRECT_URI'] = redirect_uri
        # Delete cache file
        if os.path.isfile('.cache'):
            os.remove('.cache')


def flattenArray(array):
    for sublist in array:
        for item in sublist:
            yield item
    return array



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
            result = self.sp.artist_albums(artist_id, limit=50, country=country,
                                           album_type='single,album')['items']
        else:
            result = self.sp.artist_albums(artist_id, limit=50, country=country, album_type='album,single')['items']
            loop_count = int(request_limit / 50)
            i = 0
            while len(result) < request_limit and loop_count > 0:
                new_tracks = self.sp.artist_albums(artist_id, limit=50, offset=i, country=country,
                                                   album_type='album,single')['items']
                if len(new_tracks) == 0:
                    break
                result.extend(new_tracks)
                loop_count -= 1
                i += 50

        for album in result:
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

    def generate_playlist(self, artists, tracks_per_artist, playlist_name, playlist_description, shuffle):
        self.artists = artists
        self.tracks_per_artist = tracks_per_artist
        self.playlist_name = playlist_name
        self.playlist_description = playlist_description
        self.shuffle = shuffle
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
        self.output.emit(3, f"Playlist at:", self.progress)
        self.output.emit(3, f"https://open.spotify.com/playlist/{self.playlist_id}", self.progress)

    def reset(self):
        self.progress = 0
        self.shuffle = None
        self.playlist_description = None
        self.playlist_name = None
        self.tracks_per_artist = None
        self.artists = None
        self.isGenerating = False
        self.playlist_id = None
