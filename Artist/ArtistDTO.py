from PyQt5.QtWidgets import QLabel


class ArtistDTO:
    def __init__(self, artist_id, name, image_url):
        self.artist_id = artist_id
        self.name = name
        self.image_url = image_url
        self.image_label: QLabel = None
