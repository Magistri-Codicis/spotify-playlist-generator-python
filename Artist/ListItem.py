from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from Artist.ArtistCard import ArtistCard
from Artist.ArtistListEntry import ArtistListEntry


class ListItem(QWidget):
    def __init__(self, artist: ArtistListEntry, parent=None):
        super().__init__(parent)
        self.selection_is_active = False
        self.layout = QHBoxLayout()
        self.artist_card = ArtistCard(artist, self)
        self.setLayout(self.layout)
        if artist.selected_artist is not None:
            self.name_label = QLabel(artist.result_list[artist.selected_artist].name)
        else:
            self.name_label = QLabel(artist.query)

        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(lambda: parent.delete_artist(artist))

        self.modify_button = QPushButton('Modify')
        self.modify_button.clicked.connect(lambda: self.toggleSelection(parent, artist))

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.modify_button)

    def toggleSelection(self, parent, artist: ArtistListEntry):
        if self.selection_is_active:
            self.selection_is_active = False
            self.modify_button.setText('Modify')
            artist.selected_artist = self.artist_card.selection
            self.name_label.setText(artist.result_list[artist.selected_artist].name)
            self.artist_card.setParent(None)
        else:
            self.selection_is_active = True
            self.modify_button.setText('Confirm')
            parent.artist_selection_layout.addWidget(self.artist_card)

