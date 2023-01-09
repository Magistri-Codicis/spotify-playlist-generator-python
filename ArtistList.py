from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel, QScrollArea


class ListItem(QWidget):
    def __init__(self, artist, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        if artist.selected_artist is not None:
            self.name_label = QLabel(artist.result_list[artist.selected_artist].name)
        else:
            self.name_label = QLabel(artist.query)
        self.layout.addWidget(self.name_label)


class ArtistDTO:
    def __init__(self, artist_id, name, image_url):
        self.artist_id = artist_id
        self.name = name
        self.image_url = image_url


class ArtistListEntry:
    def __init__(self, query):
        self.result_list = []
        self.query = query
        self.selected_artist = None

    def search(self, util):
        new_result_list = []
        results = util.search_artist(self.query)
        for artist in results['artists']['items']:
            artist_id = artist['id']
            name = artist['name']
            if len(artist['images']) > 0:
                image_url = artist['images'][0]['url']
            else:
                image_url = None
            new_result_list.append(ArtistDTO(artist_id, name, image_url))
        self.result_list = new_result_list
        self.selected_artist = 0


class ArtistList(QWidget):
    def __init__(self, entries=[], parent=None, util=None):
        super().__init__(parent)

        self.util = util
        self.entries = entries
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_button = QPushButton('Add')
        self.search_button.clicked.connect(self.addArtist)

        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addWidget(self.search_button)

        self.artist_list_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.artist_list_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.artist_list_layout.addWidget(self.scroll_area)

        main_layout.addLayout(self.search_layout)
        main_layout.addLayout(self.artist_list_layout)

        self.refreshList()

    def addArtist(self):
        entry = ArtistListEntry(self.search_bar.text())
        entry.search(self.util)
        self.entries.append(entry)
        self.refreshList()

    def refreshList(self):
        for entry in self.entries:
            self.artist_list_layout.addWidget(ListItem(entry))
