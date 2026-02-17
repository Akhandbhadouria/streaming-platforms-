import requests
from django.conf import settings
from datetime import datetime

class TMDBService:
    """Service to interact with TMDB API"""
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.headers = {
            'Authorization': f'Bearer {settings.TMDB_ACCESS_TOKEN}',
            'Content-Type': 'application/json;charset=utf-8'
        }
    
    def _make_request(self, endpoint, params=None):
        """Make a request to TMDB API"""
        url = f"{self.BASE_URL}{endpoint}"
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to TMDB: {e}")
            return None
    
    def get_popular_movies(self, page=1):
        """Get popular movies"""
        return self._make_request("/movie/popular", {"page": page})
    
    def get_trending_movies(self, time_window='week', page=1):
        """Get trending movies (day or week)"""
        return self._make_request(f"/trending/movie/{time_window}", {"page": page})
    
    def get_top_rated_movies(self, page=1):
        """Get top rated movies"""
        return self._make_request("/movie/top_rated", {"page": page})
    
    def get_now_playing_movies(self, page=1):
        """Get now playing movies"""
        return self._make_request("/movie/now_playing", {"page": page})
    
    def get_upcoming_movies(self, page=1):
        """Get upcoming movies"""
        return self._make_request("/movie/upcoming", {"page": page})
    
    def get_movie_details(self, movie_id):
        """Get detailed information about a movie"""
        return self._make_request(f"/movie/{movie_id}", {
            "append_to_response": "videos,credits,similar,recommendations"
        })
    
    def search_movies(self, query, page=1):
        """Search for movies"""
        return self._make_request("/search/movie", {
            "query": query,
            "page": page
        })
    
    def get_movie_videos(self, movie_id):
        """Get videos (trailers) for a movie"""
        return self._make_request(f"/movie/{movie_id}/videos")
    
    def get_genres(self):
        """Get list of movie genres"""
        return self._make_request("/genre/movie/list")
    
    def discover_movies(self, **kwargs):
        """Discover movies with filters"""
        return self._make_request("/discover/movie", kwargs)
    
    def parse_movie_data(self, movie_data):
        """Parse movie data from TMDB response"""
        try:
            release_date = None
            if movie_data.get('release_date'):
                try:
                    release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
                except ValueError:
                    release_date = None
            
            return {
                'tmdb_id': movie_data.get('id'),
                'title': movie_data.get('title', ''),
                'overview': movie_data.get('overview', ''),
                'poster_path': movie_data.get('poster_path', ''),
                'backdrop_path': movie_data.get('backdrop_path', ''),
                'release_date': release_date,
                'vote_average': movie_data.get('vote_average', 0),
                'vote_count': movie_data.get('vote_count', 0),
                'popularity': movie_data.get('popularity', 0),
                'genres': movie_data.get('genres', []) if 'genres' in movie_data else [],
                'runtime': movie_data.get('runtime'),
                'tagline': movie_data.get('tagline', ''),
                'status': movie_data.get('status', ''),
            }
        except Exception as e:
            print(f"Error parsing movie data: {e}")
            return None


class YouTubeService:
    """Service to interact with YouTube API"""
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
    
    def search_trailer(self, movie_title, year=None):
        """Search for movie trailer on YouTube"""
        query = f"{movie_title} official trailer"
        if year:
            query += f" {year}"
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'videoEmbeddable': 'true',  # Only search for embeddable videos
            'maxResults': 1,
            'key': self.api_key
        }
        
        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                return data['items'][0]['id']['videoId']
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error searching YouTube: {e}")
            return None
