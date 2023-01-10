from typing import List

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QScrollArea, QTextEdit

from Artist.ArtistCard import ArtistCard
from Artist.ArtistListEntry import ArtistListEntry
from Artist.ListItem import ListItem


class ArtistList(QWidget):
    def __init__(self, artists: List[ArtistListEntry] = [], parent=None, util=None):
        super().__init__(parent)

        self.util = util
        self.entries = artists
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.search_layout = QHBoxLayout()

        self.search_bar = QTextEdit()
        self.search_bar.setPlaceholderText('Enter Artist')
        self.search_bar.setToolTip('Enter Artist')
        self.search_bar.textChanged.connect(lambda: self.search_bar.setStyleSheet("border: 1px solid black;"))
        self.search_button = QPushButton('Add')
        self.search_button.clicked.connect(self.addArtist)
        self.search_bar.setMinimumHeight(100)

        self.search_layout.addWidget(self.search_bar)
        self.search_layout.addWidget(self.search_button)

        self.artist_selection_layout = QHBoxLayout()
        self.artist_list_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()

        self.scroll_area.setMinimumSize(800, 300)

        self.list_layout = QVBoxLayout()

        self.scroll_widget.setLayout(self.list_layout)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.artist_list_layout.addWidget(self.scroll_area)

        self.artist_selection_layout.addLayout(self.artist_list_layout)

        main_layout.addLayout(self.search_layout)
        main_layout.addLayout(self.artist_selection_layout)
        self.refreshList()

    def addArtist(self):
        query = self.search_bar.toPlainText()
        queries = []
        for line in query.splitlines():
            for comma in line.split(','):
                for semi in comma.split(';'):
                    queries.append(semi.strip())

        for query in queries:
            entry = ArtistListEntry(query)
            entry.search(self.util)
            if len(entry.result_list) > 0:
                self.entries.append(entry)
                self.list_layout.addWidget(ListItem(entry, self))
                self.search_bar.setToolTip('Enter Artist')
            else:
                try:
                    self.entries.remove(entry)
                    self.search_bar.setToolTip('No results found')
                    # make red border
                    self.search_bar.setStyleSheet("border: 1px solid red;")
                except ValueError:
                    pass

    def refreshList(self):
        self.clearList()
        for entry in self.entries:
            if len(entry.result_list) > 0:
                self.list_layout.addWidget(ListItem(entry, self))
                self.search_bar.setToolTip('Enter Artist')
            else:
                self.entries.remove(entry)
                self.search_bar.setToolTip('No results found')
                # make red border
                self.search_bar.setStyleSheet("border: 1px solid red;")

    def clearList(self):
        for i in reversed(range(self.list_layout.count())):
            self.list_layout.itemAt(i).widget().setParent(None)

    def delete_artist(self, artist):
        self.entries.remove(artist)
        self.refreshList()

    def modify_artist(self, artist: ArtistListEntry):
        self.artist_selection_layout.addWidget(ArtistCard(artist, self))
