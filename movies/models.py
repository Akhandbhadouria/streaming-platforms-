from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    """Model to store movie information from TMDB"""
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=500, blank=True, null=True)
    backdrop_path = models.CharField(max_length=500, blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0)
    genres = models.JSONField(default=list, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    tagline = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=50, blank=True)
    youtube_trailer_key = models.CharField(max_length=100, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity']

    def __str__(self):
        return self.title

    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def backdrop_url(self):
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/original{self.backdrop_path}"
        return None


class Watchlist(models.Model):
    """User's watchlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"



class MovieView(models.Model):
    """Model to track movie views for analytics"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.movie.title} viewed at {self.viewed_at}"
