import spotipy

    def rip_spotify_list(self, type):

        if type == "playlist":
            search = self.args.playlist

        elif type == "album":
            search = self.args.album

        if self.args.artist:
            search += self.args.artist

        try:
            client_credentials_manager = SpotifyClientCredentials(CONFIG["client_id"], CONFIG["client_secret"])
            spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except spotipy.oauth2.SpotifyOauthError:
            spotify = spotipy.Spotify()

        results = spotify.search(q=search, type=type)
        items = results[type + "s"]['items']
        songs = []
        if len(items) > 0:
            spotify_list = choose_from_spotify_list(items)
            list_type = spotify_list["type"]
            if list_type != "playlist":
                spotify_list = eval("spotify.%s" % list_type)(spotify_list["uri"])
            else:
                try:
                    spotify_list = spotify.user_playlist(spotify_list["owner"]["id"], \
                    playlist_id=spotify_list["uri"], fields="tracks,next")
                except spotipy.client.SpotifyException:
                    print (bc.FAIL + "To download Spotify playlists, you need to supply client_ids." + bc.ENDC)
                    print ("To do this, you'll want to create an application here:")
                    print ("https://developer.spotify.com/my-applications/#!/applications/create")
                    print ("Once you've done that, you'll want to copy your 'client id' and your 'client secret'")
                    print ("into the config file and their corresponding locations:")
                    print (get_config_file_path())
                    exit(1)

            print (bc.YELLOW + "\nFetching tracks and their metadata: " + bc.ENDC)

            increment = 0

            for song in spotify_list["tracks"]["items"]:

                increment += 1
                list_size = increment / len(spotify_list["tracks"]["items"])
                drawProgressBar(list_size)

                if list_type == "playlist":
                    song = song["track"]

                artist = spotify.artist(song["artists"][0]["id"])


                if list_type == "playlist":
                    album = (spotify.track(song["uri"])["album"])
                else:
                    album = spotify_list

                songs.append({
                    "name": song["name"],
                    "artist": artist["name"],
                    "album": album["name"],
                    "tracknum": song["track_number"],
                    "album_cover": album["images"][0]["url"]
                })

            print (bc.OKGREEN + "\nFound tracks:" + bc.ENDC)

            print (bc.HEADER)
            for song in songs:
                print ("\t" + song["name"] + " - " + song["artist"])
            print (bc.ENDC + "\n")

            for song in songs:
                self.rip_mp3(song["name"], song["artist"], album=song["album"], \
                tracknum=song["tracknum"], album_art_url=song["album_cover"])

        else:
            print (bc.FAIL + "No results were found. Make sure to use proper spelling and capitalization." + bc.ENDC)
            exit(1)
