import sys
from PyQt5.QtWidgets import QApplication, QWidget, QBoxLayout, QPushButton, QLabel

import Util
from Artist.ArtistList import ArtistList


class App:
    def __init__(self):
        self.util = Util.Util()
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.window.setLayout(self.main_layout)
        self.window.setWindowTitle('Spotify Playlist Generator')
        self.username_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.login_button = QPushButton('Login')
        if self.util.username:
            self.username_label = QLabel('Username: ' + self.util.username)
        else:
            self.username_label = QLabel('Username: ')
        self.login_button.clicked.connect(self.login)
        self.username_layout.addWidget(self.username_label)
        self.username_layout.addWidget(self.login_button)

        self.artist_selection_layout = QBoxLayout(QBoxLayout.LeftToRight)

        self.artist_list = ArtistList(util=self.util)
        self.artist_selection_layout.addWidget(self.artist_list)

        self.main_layout.addLayout(self.username_layout)

        self.window.show()
        self.app.exec_()

    def loginCallback(self):
        self.main_layout.addLayout(self.artist_selection_layout)

    def login(self):
        self.util.authenticate()
        if self.util.username:
            self.username_label.setText("Username: " + self.util.username)
            self.login_button.setEnabled(False)
            self.username_layout.removeWidget(self.login_button)
            self.login_button.deleteLater()
            self.loginCallback()


if __name__ == '__main__':
    app = App()
