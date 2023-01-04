import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, \
    QCheckBox, QListWidget, QListWidgetItem, QSizePolicy
from Util import Util


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_result = None
        self.search_results_list = None
        self.result_label = None
        self.shuffle_checkbox = None
        self.playlist_name_textbox = None
        self.playlist_name_label = None
        self.generate_button = None
        self.tracks_textbox = None
        self.tracks_label = None
        self.selected_artists_label = None
        self.selected_artists = None
        self.search_results = None
        self.confirm_button = None
        self.search_results_text = None
        self.search_results_label = None
        self.search_button = None
        self.textbox = None
        self.label = None
        self.title = 'Spotify Playlist Generator'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.styleSheet = 'QLabel {' \
                          'background-color: #1DB954;' \
                          'color: #FFFFFF;' \
                          'font-size: 16px;' \
                          'font-family: Arial;' \
                          'width: 200px' \
                          '}'
        self.initUI()

    def initUI(self):
        self.setStyleSheet(self.styleSheet)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create a label for the artist input field
        self.label = QLabel(self)
        self.label.setText('Enter artist names:')
        self.label.move(20, 20)

        # Create a text input field for the artist names
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 50)
        self.textbox.resize(280, 40)

        # Create a button to search for the artists
        self.search_button = QPushButton('Search', self)
        self.search_button.move(20, 100)
        self.search_button.clicked.connect(self.on_search)

        # Create a label to display the search results
        self.search_results_label = QLabel(self)
        self.search_results_label.move(20, 150)

        # Create a list widget to display the search results
        self.search_results_list = QListWidget(self)
        self.search_results_list.move(20, 180)
        self.search_results_list.resize(280, 200)
        self.search_results_list.itemClicked.connect(self.on_select)

        # Create a button to confirm the selected artists
        self.confirm_button = QPushButton('Confirm', self)
        self.confirm_button.move(20, 400)
        self.confirm_button.clicked.connect(self.on_confirm)
        self.confirm_button.setEnabled(False)

        # Create a label to display the selected artists
        self.selected_artists_label = QLabel(self)
        self.selected_artists_label.move(20, 430)

        # Create a label for the tracks per artist input field
        self.tracks_label = QLabel(self)
        self.tracks_label.setText('Enter number of tracks per artist:')
        self.tracks_label.move(320, 20)

        # Create a text input field for the number of tracks per artist
        self.tracks_textbox = QLineEdit(self)
        self.tracks_textbox.move(320, 50)
        self.tracks_textbox.resize(280, 40)

        # Create a button to generate the playlist
        self.generate_button = QPushButton('Generate playlist', self)
        self.generate_button.move(320, 100)

        # Create a label for the playlist name input field
        self.playlist_name_label = QLabel(self)
        self.playlist_name_label.setText('Enter playlist name:')
        self.playlist_name_label.move(320, 150)

        # Create a text input field for the playlist name
        self.playlist_name_textbox = QLineEdit(self)
        self.playlist_name_textbox.move(320, 180)
        self.playlist_name_textbox.resize(280, 40)

        # Create a checkbox to allow shuffling of tracks
        self.shuffle_checkbox = QCheckBox('Shuffle tracks', self)
        self.shuffle_checkbox.move(320, 230)

        # Create a label to display the result
        self.result_label = QLabel(self)
        self.result_label.move(320, 270)

        self.show()

    def on_search(self):
        # Clear the list widget
        self.search_results_list.clear()

        # Get the artist names from the text input field
        artist_names = self.textbox.text().split(',')

        # Create an instance of the Util class
        util = Util()

        # Search for the artists and get their IDs
        result = util.search_artists(artist_names)
        self.search_results = {}
        for artist, artist_results in zip(artist_names, result):
            self.search_results[artist] = artist_results['artists']['items']
            # Add the search results to the list widget
            for artist_item in self.search_results[artist][:3]:
                item = QListWidgetItem(artist_item['name'])
                self.search_results_list.addItem(item)

        # Enable the confirm button
        self.confirm_button.setEnabled(True)

    def on_select(self, item):
        # Get the artist name and search results
        artist = list(self.search_results.keys())[0]
        search_results = self.search_results[artist]

        # Find the selected search result
        for i, result in enumerate(search_results):
            if result['name'] == item.text():
                self.selected_result = result
                break
        print("Result selected: " + str(self.selected_result))
        # Update the search results label
        self.search_results_label.setText('Selected: ' + self.selected_result['name'])

    def on_confirm(self):
        # Clear the selected artists label
        self.selected_artists_label.setText('')

        # Add the selected artist to the list of selected artists
        self.selected_artists = {list(self.search_results.keys())[0]: self.selected_result['id']}
        self.selected_artists_label.setText(f"{list(self.search_results.keys())[0]}: {self.selected_result['name']}\n")

        # Enable the generate button
        self.generate_button.setEnabled(True)

    def on_generate(self):
        # Get the number of tracks per artist from the text input field
        tracks_per_artist = int(self.tracks_textbox.text())

        # Get the playlist name from the text input field
        playlist_name = self.playlist_name_textbox.text()

        # Get the shuffle setting from the checkbox
        shuffle = self.shuffle_checkbox.isChecked()

        # Create an instance of the Util class
        util = Util()

        # Get the top tracks for each selected artist
        tracks = util.get_all_tracks(self.selected_artists, tracks_per_artist, shuffle)

        # Create the playlist
        util.create_playlist(playlist_name)

        # Add the tracks to the playlist
        util.add_tracks(tracks)

        # Display the result
        playlist_url = f"https://open.spotify.com/playlist/{util.playlist_id}"
        self.result_label.setText(
            f'Playlist "{playlist_name}" created with {len(tracks)} tracks!\nPlaylist URL: {playlist_url}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
