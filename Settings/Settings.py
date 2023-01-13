from PyQt5.QtWidgets import QWidget, QBoxLayout, QLineEdit, QTextEdit, QSpinBox, QCheckBox, QPushButton, QLabel


class Settings(QWidget):
    def __init__(self, util, parent=None, artist_list=None):
        super().__init__(parent)
        self.playlist_url = None
        self.util = util
        self.artist_list = artist_list
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

        self.song_count_label = QLabel("Song Count")
        self.playlist_name_label = QLabel("Playlist Name")
        self.playlist_description_label = QLabel("Playlist Description")

        self.song_count_input.setToolTip("The number of songs to add to of each artist")
        self.playlist_name_input.setToolTip("The name of the playlist to create")
        self.playlist_description_input.setToolTip("The description of the playlist to create")
        self.do_shuffle_input.setToolTip("Whether or not to shuffle the playlist")

        self.do_shuffle_input.setText("Shuffle Playlist")

        self.output_layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.output_label = QLabel("Output")
        self.output_scroll = QTextEdit()
        self.output_scroll.setReadOnly(True)

        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_scroll)

        self.main_layout.addWidget(self.song_count_label)
        self.main_layout.addWidget(self.song_count_input)

        self.main_layout.addWidget(self.playlist_name_label)
        self.main_layout.addWidget(self.playlist_name_input)

        self.main_layout.addWidget(self.playlist_description_label)
        self.main_layout.addWidget(self.playlist_description_input)

        self.main_layout.addWidget(self.do_shuffle_input)
        self.main_layout.addWidget(self.generate_button)

        self.main_layout.addLayout(self.output_layout)

        self.generate_button.clicked.connect(self.generatePlaylist)

    def generatePlaylist(self):
        self.output_scroll.clear()
        self.song_count = self.song_count_input.value()
        self.playlist_name = self.playlist_name_input.text()
        self.playlist_description = self.playlist_description_input.toPlainText()
        self.do_shuffle = self.do_shuffle_input.isChecked()
        self.playlist_url = self.util.generate_playlist(self.artist_list, self.song_count, self.playlist_name,
                                                        self.playlist_description,
                                                        self.do_shuffle, self.output_scroll)
