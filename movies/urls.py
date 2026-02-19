from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse_movies, name='browse'),
    path('search/', views.search_movies, name='search'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
    path('profile/', views.profile, name='profile'),
    path('movie/toggle-hide/<int:movie_id>/', views.toggle_hide_movie, name='toggle_hide_movie'),
    path('supervisor-portal/', views.supervisor_dashboard, name='supervisor_dashboard'),
]
