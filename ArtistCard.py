from PyQt5.QtCore import QUrl, QEventLoop
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy, QRadioButton


def getImageData(url):
    manager = QNetworkAccessManager()
    request = QNetworkRequest(QUrl(url))
    reply = manager.get(request)
    loop = QEventLoop()
    reply.finished.connect(loop.quit)
    loop.exec_()
    return reply.readAll()


class CardComponent(QWidget):
    def __init__(self, title, entries, parent=None):
        super().__init__(parent)

        # Create main layout
        main_layout = QVBoxLayout()

        # Add title label
        title_label = QLabel(title)
        main_layout.addWidget(title_label)

        # Create network manager
        self.network_manager = QNetworkAccessManager(self)

        # Add entries
        for entry in entries:
            entry_layout = QHBoxLayout()
            thumbnail_label = QLabel()
            thumbnail_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            name_label = QLabel(entry['name'])
            select_button = QRadioButton()
            entry_layout.addWidget(thumbnail_label)
            entry_layout.addWidget(name_label)
            entry_layout.addWidget(select_button)
            main_layout.addLayout(entry_layout)

            # Store reference to thumbnail label in entry
            entry['thumbnail_label'] = thumbnail_label

            # Update thumbnail label with image data
            image_data = getImageData(entry['thumbnail_url'])
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            thumbnail_label.setPixmap(pixmap)

        # Set main layout
        self.setLayout(main_layout)
