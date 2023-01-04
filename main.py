import Util

# Set environment variables from a file
util = Util.Util()

print("Welcome " + util.username)

# Step 1: get list of artists from user
artists = input("Enter a list of artists, separated by commas: ").split(',')

# Step 2: search for each artist and provide first 3 results
search_result = util.search_artists(artist_list=artists)
for search_artist, artist_results in zip(artists, search_result):
    print(f"Results for {search_artist}:")
    for i, artist in enumerate(artist_results['artists']['items'][:3]):
        print(f"{i + 1}. {artist['name']}")

# Step 3: get user to select correct search result for each artist
selected_artists = {}
for artist, result in zip(artists, search_result):
    selection = int(input(f"Enter the number of the correct search result for {artist}: "))
    selected_artists[artist] = result['artists']['items'][selection - 1]['id']

# Step 4: get number of tracks per artist from user
tracks_per_artist = int(input("Enter the number of tracks per artist: "))

# Step 5: show total number of tracks and get user confirmation
total_tracks = len(artists) * int(tracks_per_artist)
print(f"This will add a total of {total_tracks} tracks to the playlist.")
confirmation = input("Enter 'y' to confirm: ")
if confirmation != 'y':
    exit()

# Step 6: get playlist name from user
playlist_name = input("Enter a name for the playlist: ")

# Step 7: create playlist and add tracks

shuffle = input("Shuffle tracks? (y/n): ")
# get all tracks
tracks = util.get_all_tracks(selected_artists, 10, shuffle == 'y')

# create playlist
util.create_playlist(playlist_name)

# add tracks to playlist

util.add_tracks(tracks)

# Step 8: display success message with playlist URL
playlist_url = f"https://open.spotify.com/playlist/{util.playlist_id}"
print(f"Playlist successfully created at {playlist_url}")
