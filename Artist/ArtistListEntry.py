from typing import List

from Artist.ArtistDTO import ArtistDTO


class ArtistListEntry:
    def __init__(self, query):
        self.result_list: List[ArtistDTO] = []
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

    def selectArtist(self, index):
        self.selected_artist = index
