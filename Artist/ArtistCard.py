from PyQt5.QtCore import QUrl, QEventLoop, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy, QRadioButton

from Artist.ArtistListEntry import ArtistListEntry


def getImageData(url):
    manager = QNetworkAccessManager()
    request = QNetworkRequest(QUrl(url))
    reply = manager.get(request)
    loop = QEventLoop()
    reply.finished.connect(loop.quit)
    loop.exec_()
    return reply.readAll()


class ArtistCard(QWidget):
    def __init__(self, artist: ArtistListEntry, parent=None):
        super().__init__(parent)

        # Create main layout
        main_layout = QVBoxLayout()

        # Add title label
        title_label = QLabel("You searched for: " + artist.query)
        main_layout.addWidget(title_label)

        # Create network manager
        self.network_manager = QNetworkAccessManager(self)

        self.selection = artist.selected_artist

        for result_item in artist.result_list:
            entry_layout = QHBoxLayout()
            thumbnail_label = QLabel()
            thumbnail_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            name_label = QLabel(result_item.name)
            select_button = QRadioButton()
            select_button.setChecked(artist.selected_artist == artist.result_list.index(result_item))
            select_button.index = artist.result_list.index(result_item)
            select_button.toggled.connect(self.select)
            entry_layout.addWidget(thumbnail_label)
            entry_layout.addWidget(name_label)
            entry_layout.addWidget(select_button)
            main_layout.addLayout(entry_layout)

            # Store reference to thumbnail label in result_item
            result_item.thumbnail_label = thumbnail_label

            # Update thumbnail label with image data
            image_data = getImageData(result_item.image_url)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            pixmap = pixmap.scaledToWidth(200)
            # Make the pixmap round
            mask = QPixmap(pixmap.size())
            mask.fill(Qt.transparent)
            painter = QPainter(mask)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.black)
            painter.drawRoundedRect(QRect(0, 0, 200, 200), 50, 50)
            painter.end()
            pixmap.setMask(mask.mask())
            thumbnail_label.setPixmap(pixmap)

        # Set main layout
        self.setLayout(main_layout)

    def select(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            self.selection = radio_button.index
