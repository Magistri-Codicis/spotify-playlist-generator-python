from PyQt5.QtWidgets import QWidget, QBoxLayout, QLineEdit, QTextEdit, QSpinBox, QCheckBox, QPushButton


class Settings(QWidget):
    def __init__(self, util, parent=None):
        super().__init__(parent)
        self.util = util
        self.main_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(self.main_layout)
        self.song_count = 5
        self.playlist_name = "My Playlist"
        self.playlist_description = "My Playlist Description"
        self.do_shuffle = False

        self.song_count_input = QSpinBox()
        self.playlist_name_input = QLineEdit()
        self.playlist_description_input = QTextEdit()
        self.do_shuffle_input = QCheckBox()
        self.generate_button = QPushButton("Generate Playlist")

        self.song_count_input.setValue(self.song_count)
        self.playlist_name_input.setText(self.playlist_name)
        self.playlist_description_input.setText(self.playlist_description)
        self.do_shuffle_input.setChecked(self.do_shuffle)

        self.main_layout.addWidget(self.song_count_input)
        self.main_layout.addWidget(self.playlist_name_input)
        self.main_layout.addWidget(self.playlist_description_input)
        self.main_layout.addWidget(self.do_shuffle_input)
        self.main_layout.addWidget(self.generate_button)

        self.generate_button.clicked.connect(self.generatePlaylist)

    def generatePlaylist(self):
        self.song_count = self.song_count_input.value()
        self.playlist_name = self.playlist_name_input.text()
        self.playlist_description = self.playlist_description_input.toPlainText()
        self.do_shuffle = self.do_shuffle_input.isChecked()
        self.util.generatePlaylist(self.song_count, self.playlist_name, self.playlist_description, self.do_shuffle)






