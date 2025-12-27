import requests
import json
import base64
from pydantic import BaseModel, Field

class Tools:
    class Valves(BaseModel):
        SPOTIFY_CLIENT_ID: str = Field(
            default="", description="Your Spotify App Client ID"
        )
        SPOTIFY_CLIENT_SECRET: str = Field(
            default="", description="Your Spotify App Client Secret"
        )
        COUNTRY_CODE: str = Field(
            default="TW", description="ISO 3166-1 alpha-2 country code (e.g. TW, US)"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _get_headers(self) -> dict:
        """
        Internal helper to authenticate and get headers.
        """
        if not self.valves.SPOTIFY_CLIENT_ID or not self.valves.SPOTIFY_CLIENT_SECRET:
            raise Exception("Spotify Client ID and Secret not set in Valves.")

        auth_string = f"{self.valves.SPOTIFY_CLIENT_ID}:{self.valves.SPOTIFY_CLIENT_SECRET}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token = response.json()["access_token"]
        return {"Authorization": "Bearer " + token}

    def search_spotify(self, query: str, search_type: str = "track") -> str:
        """
        Search for a track, artist, album, or playlist on Spotify.
        Results now include release date.
        
        :param query: The search term.
        :param search_type: 'track', 'artist', 'album', 'playlist'.
        :return: JSON string of results.
        """
        try:
            headers = self._get_headers()
            params = {
                "q": query,
                "type": search_type,
                "limit": 5,
                "market": self.valves.COUNTRY_CODE
            }
            response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if search_type == "track" and "tracks" in data:
                for item in data["tracks"]["items"]:
                    r_date = item['album'].get('release_date', 'Unknown')
                    results.append(f"Track: {item['name']} - Artist: {item['artists'][0]['name']} (Released: {r_date})")
            elif search_type == "artist" and "artists" in data:
                for item in data["artists"]["items"]:
                    results.append(f"Artist: {item['name']} (Popularity: {item['popularity']})")
            elif search_type == "album" and "albums" in data:
                for item in data["albums"]["items"]:
                    r_date = item.get('release_date', 'Unknown')
                    results.append(f"Album: {item['name']} - Artist: {item['artists'][0]['name']} (Released: {r_date})")
            
            return json.dumps(results, indent=2) if results else "No results found."

        except Exception as e:
            return f"Error performing search: {str(e)}"

    def search_spotify_multiple(self, queries: list[str], search_type: str = "track") -> str:
        """
        Search for multiple items at once. Useful when users ask about a list of specific songs or artists.
        
        :param queries: A list of search terms (e.g. ['Hello', 'Rolling in the Deep']).
        :param search_type: 'track', 'artist', or 'album'.
        :return: A combined string of results for all queries.
        """
        combined_results = []
        headers = self._get_headers()
        url = "https://api.spotify.com/v1/search"

        for q in queries:
            try:
                params = {
                    "q": q,
                    "type": search_type,
                    "limit": 1, # Limit to 1 per query to keep context small
                    "market": self.valves.COUNTRY_CODE
                }
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if search_type == "track" and "tracks" in data and data["tracks"]["items"]:
                    item = data["tracks"]["items"][0]
                    r_date = item['album'].get('release_date', 'Unknown')
                    combined_results.append(f"Query '{q}': Found '{item['name']}' by {item['artists'][0]['name']} (Released: {r_date})")
                
                elif search_type == "artist" and "artists" in data and data["artists"]["items"]:
                    item = data["artists"]["items"][0]
                    combined_results.append(f"Query '{q}': Found Artist '{item['name']}' (Popularity: {item['popularity']})")
                    
                elif search_type == "album" and "albums" in data and data["albums"]["items"]:
                    item = data["albums"]["items"][0]
                    r_date = item.get('release_date', 'Unknown')
                    combined_results.append(f"Query '{q}': Found Album '{item['name']}' by {item['artists'][0]['name']} (Released: {r_date})")
                else:
                    combined_results.append(f"Query '{q}': No results found.")

            except Exception as e:
                combined_results.append(f"Query '{q}': Error {str(e)}")
        
        return "\n".join(combined_results)

    def get_artist_tracks_by_genre(self, artist_name: str, genre: str) -> str:
        """
        Find tracks by a specific artist that fit a specific genre.
        Like finding 'pop' songs by 'Drake' or 'rock' songs by 'Miley Cyrus'.
        
        :param artist_name: Name of the artist.
        :param genre: The specific genre tag (e.g. pop, rock, house).
        :return: List of tracks with release dates.
        """
        # We construct the specific advanced query: artist:Name genre:Name
        query = f"artist:{artist_name} genre:{genre}"
        return self.search_spotify(query, "track")

    def get_artist_top_tracks(self, artist_name: str) -> str:
        """
        Get the top popular tracks for a specific artist name.
        
        :param artist_name: The name of the artist (e.g., 'Ed Sheeran').
        :return: A list of the artist's top 10 tracks.
        """
        try:
            headers = self._get_headers()
            
            # Step 1: Search for the artist
            search_url = "https://api.spotify.com/v1/search"
            search_params = {"q": artist_name, "type": "artist", "limit": 1}
            search_res = requests.get(search_url, headers=headers, params=search_params)
            search_data = search_res.json()
            
            if not search_data["artists"]["items"]:
                return f"Could not find artist: {artist_name}"
            
            artist_id = search_data["artists"]["items"][0]["id"]
            real_name = search_data["artists"]["items"][0]["name"]
            
            # Step 2: Get Top Tracks
            top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
            tt_params = {"market": self.valves.COUNTRY_CODE}
            tt_res = requests.get(top_tracks_url, headers=headers, params=tt_params)
            tt_data = tt_res.json()
            
            # Added release_date here as well
            tracks = []
            for t in tt_data['tracks']:
                r_date = t['album'].get('release_date', 'Unknown')
                tracks.append(f"{t['name']} (Album: {t['album']['name']}, Released: {r_date})")

            return f"Top tracks for {real_name}:\n" + "\n".join(tracks)

        except Exception as e:
            return f"Error fetching top tracks: {str(e)}"
        
    def get_tracks_by_genre(self, genre: str) -> str:
        """
        Find songs based on a specific genre.
        
        :param genre: The genre to search for (e.g., 'pop', 'jazz', 'rock').
        :return: A list of tracks matching the genre.
        """
        # This uses the specific "genre:" syntax logic discussed previously
        return self.search_spotify(f"genre:{genre}", "track")
    
    def get_album_tracklist(self, album_name: str) -> str:
        """
        Get the list of songs on a specific album.
        
        :param album_name: The name of the album to look up.
        :return: A list of track names and their duration.
        """
        try:
            headers = self._get_headers()
            
            search_url = "https://api.spotify.com/v1/search"
            search_params = {"q": album_name, "type": "album", "limit": 1}
            search_res = requests.get(search_url, headers=headers, params=search_params)
            search_data = search_res.json()
            
            if not search_data["albums"]["items"]:
                return f"Could not find album: {album_name}"
            
            album_id = search_data["albums"]["items"][0]["id"]
            real_album_name = search_data["albums"]["items"][0]["name"]
            # Album object usually has the release date at the top level
            album_release_date = search_data["albums"]["items"][0].get("release_date", "Unknown")
            
            tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
            tracks_params = {"limit": 20, "market": self.valves.COUNTRY_CODE}
            tracks_res = requests.get(tracks_url, headers=headers, params=tracks_params)
            tracks_data = tracks_res.json()
            
            track_list = []
            for item in tracks_data["items"]:
                duration_min = item["duration_ms"] / 1000 / 60
                track_list.append(f"{item['track_number']}. {item['name']} ({duration_min:.2f} min)")
                
            return f"Tracklist for '{real_album_name}' (Released: {album_release_date}):\n" + "\n".join(track_list)

        except Exception as e:
            return f"Error fetching album info: {str(e)}"
    
    def get_artist_discography(self, artist_name: str, limit: int = 10) -> str:
        """
        Get a list of an artist's releases (Albums and Singles), sorted by release date (newest first).
        Useful for finding the 'newest song', 'latest album', or seeing an artist's history.
        
        :param artist_name: Name of the artist.
        :param limit: Number of releases to return (default 10).
        :return: List of releases sorted by date descending.
        """
        try:
            headers = self._get_headers()
            
            # Step 1: Get Artist ID
            search_url = "https://api.spotify.com/v1/search"
            search_params = {"q": artist_name, "type": "artist", "limit": 1}
            search_res = requests.get(search_url, headers=headers, params=search_params)
            search_data = search_res.json()
            
            if not search_data["artists"]["items"]:
                return f"Could not find artist: {artist_name}"
            
            artist_id = search_data["artists"]["items"][0]["id"]
            artist_real_name = search_data["artists"]["items"][0]["name"]

            # Step 2: Get Artist Albums (we request both 'album' and 'single')
            albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
            albums_params = {
                "include_groups": "album,single", 
                "limit": 50,  # Request more to ensure we get the latest
                "market": self.valves.COUNTRY_CODE
            }
            
            albums_res = requests.get(albums_url, headers=headers, params=albums_params)
            albums_data = albums_res.json()
            
            items = albums_data["items"]
            
            # Step 3: Manual Sort by Release Date (Newest First)
            # API sort is usually good, but manual sort guarantees accuracy for "newest"
            items.sort(key=lambda x: x['release_date'], reverse=True)
            
            results = []
            for item in items[:limit]:
                r_date = item.get('release_date', 'Unknown')
                r_type = item.get('album_type', 'album')
                results.append(f"{r_date}: {item['name']} ({r_type})")

            return f"Most recent releases by {artist_real_name}:\n" + "\n".join(results)

        except Exception as e:
            return f"Error fetching discography: {str(e)}"


