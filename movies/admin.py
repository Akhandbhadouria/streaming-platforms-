from django.contrib import admin
from .models import Movie, Watchlist, MovieView

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'vote_average', 'popularity', 'status')
    search_fields = ('title', 'tmdb_id')
    list_filter = ('release_date', 'status')
    ordering = ('-popularity',)

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('added_at',)



@admin.register(MovieView)
class MovieViewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'ip_address', 'viewed_at')
    search_fields = ('movie__title', 'user__username', 'ip_address')
    list_filter = ('viewed_at',)
    readonly_fields = ('movie', 'user', 'ip_address', 'viewed_at')
    ordering = ('-viewed_at',)

