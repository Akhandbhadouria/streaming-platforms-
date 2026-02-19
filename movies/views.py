from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Movie, Watchlist, Rating, MovieView
from .services import TMDBService, YouTubeService
from .forms import RatingForm
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta

# Configure logger
logger = logging.getLogger(__name__)

tmdb_service = TMDBService()
youtube_service = YouTubeService()

def _filter_hidden_movies(request, movies_list):
    """Helper to filter out hidden movies from API results for regular users"""
    if request.user.is_authenticated and request.user.is_staff:
        # Supervisors can see everything
        return movies_list
    
    hidden_ids = Movie.objects.filter(is_hidden=True).values_list('tmdb_id', flat=True)
    return [m for m in movies_list if m.get('id') not in hidden_ids]

def home(request):
    """Home page with featured movies"""
    # Get trending movies with error handling
    try:
        trending_data = tmdb_service.get_trending_movies()
        popular_data = tmdb_service.get_popular_movies()
        top_rated_data = tmdb_service.get_top_rated_movies()
    except Exception as e:
        logger.error(f"Error fetching home page movies: {e}")
        trending_data = None
        popular_data = None
        top_rated_data = None
    
    trending = trending_data.get('results', []) if trending_data else []
    popular = popular_data.get('results', []) if popular_data else []
    top_rated = top_rated_data.get('results', []) if top_rated_data else []

    # Top 5 Viewed Movies Today
    today = timezone.now().date()
    top_today = Movie.objects.filter(
        views__viewed_at__date=today,
        is_hidden=False
    ).annotate(
        today_views=Count('views')
    ).order_by('-today_views')[:5]

    context = {
        'trending_movies': _filter_hidden_movies(request, trending)[:20],
        'popular_movies': _filter_hidden_movies(request, popular)[:20],
        'top_rated_movies': _filter_hidden_movies(request, top_rated)[:20],
        'top_today': top_today,
        'hidden_movies_ids': list(Movie.objects.filter(is_hidden=True).values_list('tmdb_id', flat=True)) if request.user.is_staff else []
    }
    
    return render(request, 'movies/home.html', context)


def browse_movies(request):
    """Browse all movies with filters"""
    page = request.GET.get('page', 1)
    category = request.GET.get('category', 'popular')
    
    if category == 'trending':
        data = tmdb_service.get_trending_movies(page=page)
    elif category == 'top_rated':
        data = tmdb_service.get_top_rated_movies(page=page)
    elif category == 'upcoming':
        data = tmdb_service.get_upcoming_movies(page=page)
    elif category == 'now_playing':
        data = tmdb_service.get_now_playing_movies(page=page)
    else:
        data = tmdb_service.get_popular_movies(page=page)
    
    movies = data.get('results', []) if data else []
    filtered_movies = _filter_hidden_movies(request, movies)
    total_pages = data.get('total_pages', 1) if data else 1
    
    context = {
        'movies': filtered_movies,
        'category': category,
        'current_page': int(page),
        'total_pages': min(total_pages, 500),  # TMDB limits to 500 pages
        'hidden_movies_ids': list(Movie.objects.filter(is_hidden=True).values_list('tmdb_id', flat=True)) if request.user.is_staff else []
    }
    
    return render(request, 'movies/browse.html', context)


def movie_detail(request, movie_id):
    """Movie detail page"""
    # Get movie details from TMDB with error handling for SSL and network issues
    try:
        movie_data = tmdb_service.get_movie_details(movie_id)
    except Exception as e:
        logger.error(f"Error fetching movie details for {movie_id}: {e}")
        return render(request, 'movies/error.html', {
            'message': 'Unable to load movie details. The movie database is temporarily unavailable. Please try again in a few moments.'
        })
    
    if not movie_data:
        return render(request, 'movies/error.html', {'message': 'Movie not found'})
    
    # Get or create movie in database
    movie, created = Movie.objects.get_or_create(
        tmdb_id=movie_id,
        defaults=tmdb_service.parse_movie_data(movie_data)
    )

    # Check if movie is hidden and user is not staff
    if movie.is_hidden and not (request.user.is_authenticated and request.user.is_staff):
        return render(request, 'movies/error.html', {'message': 'This movie is currently restricted.'})
    
    # Get YouTube trailer
   # Only check and save trailer if not already saved
    if not movie.youtube_trailer_key:

        videos = movie_data.get('videos', {}).get('results', [])

        youtube_trailers = [
            v for v in videos
            if v.get('site') == 'YouTube'
            and v.get('type') == 'Trailer'
        ]

        selected_trailer = None

        for v in youtube_trailers:
            if youtube_service.is_embeddable(v['key']):
                selected_trailer = v
                break

        if selected_trailer:
            movie.youtube_trailer_key = selected_trailer['key']
            movie.save()

    # Check if movie is in user's watchlist
    in_watchlist = False
    user_rating = None
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, movie=movie).exists()
        try:
            user_rating = Rating.objects.get(user=request.user, movie=movie)
        except Rating.DoesNotExist:
            pass
            
    # Track view for analytics
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    MovieView.objects.create(
        movie=movie,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip
    )
    
    context = {
        'movie': movie,
        'movie_data': movie_data,
        'in_watchlist': in_watchlist,
        'user_rating': user_rating,
        'cast': movie_data.get('credits', {}).get('cast', [])[:10],
        'similar_movies': movie_data.get('similar', {}).get('results', [])[:6],
    }
    
    return render(request, 'movies/detail.html', context)


def search_movies(request):
    """Search movies"""
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    
    if query:
        data = tmdb_service.search_movies(query, page=page)
        movies = data.get('results', []) if data else []
        filtered_movies = _filter_hidden_movies(request, movies)
        total_pages = data.get('total_pages', 1) if data else 1
        total_results = data.get('total_results', 0) if data else 0
    else:
        filtered_movies = []
        total_pages = 1
        total_results = 0
    
    context = {
        'movies': filtered_movies,
        'query': query,
        'current_page': int(page),
        'total_pages': min(total_pages, 500),
        'total_results': total_results,
        'hidden_movies_ids': list(Movie.objects.filter(is_hidden=True).values_list('tmdb_id', flat=True)) if request.user.is_staff else []
    }
    
    return render(request, 'movies/search.html', context)


@login_required
def watchlist(request):
    """User's watchlist"""
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('movie')
    
    context = {
        'watchlist_items': watchlist_items,
    }
    
    return render(request, 'movies/watchlist.html', context)


@login_required
def add_to_watchlist(request, movie_id):
    """Add movie to watchlist"""
    if request.method == 'POST':
        # Get or create movie in database
        movie_data = tmdb_service.get_movie_details(movie_id)
        if movie_data:
            defaults = tmdb_service.parse_movie_data(movie_data)
            if defaults:
                # Remove tmdb_id from defaults if present to avoid conflict
                defaults.pop('tmdb_id', None)
                
                movie, created = Movie.objects.get_or_create(
                    tmdb_id=movie_id,
                    defaults=defaults
                )
                
                # Add to watchlist
                Watchlist.objects.get_or_create(user=request.user, movie=movie)
                
                return JsonResponse({'status': 'success', 'message': 'Added to watchlist'})
            else:
                 return JsonResponse({'status': 'error', 'message': 'Failed to parse movie data'}, status=500)
        
        return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def remove_from_watchlist(request, movie_id):
    """Remove movie from watchlist"""
    if request.method == 'POST':
        try:
            movie = Movie.objects.get(tmdb_id=movie_id)
            Watchlist.objects.filter(user=request.user, movie=movie).delete()
            return JsonResponse({'status': 'success', 'message': 'Removed from watchlist'})
        except Movie.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def rate_movie(request, movie_id):
    """Rate a movie"""
    if request.method == 'POST':
        try:
            movie = Movie.objects.get(tmdb_id=movie_id)
            
            # Try to get existing rating
            try:
                rating_obj = Rating.objects.get(user=request.user, movie=movie)
                form = RatingForm(request.POST, instance=rating_obj)
            except Rating.DoesNotExist:
                form = RatingForm(request.POST)
            
            if form.is_valid():
                rating_obj = form.save(commit=False)
                rating_obj.user = request.user
                rating_obj.movie = movie
                rating_obj.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Rating saved',
                    'rating': rating_obj.rating
                })
            else:
                # Return form errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid rating',
                    'errors': form.errors
                }, status=400)
                
        except Movie.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@staff_member_required
def toggle_hide_movie(request, movie_id):
    """Toggle a movie's hidden status (Supervisor only)"""
    if request.method == 'POST':
        # Get or create movie in database
        movie_data = tmdb_service.get_movie_details(movie_id)
        if movie_data:
            movie, created = Movie.objects.get_or_create(
                tmdb_id=movie_id,
                defaults=tmdb_service.parse_movie_data(movie_data)
            )
            
            movie.is_hidden = not movie.is_hidden
            movie.save()
            
            status = "hidden" if movie.is_hidden else "visible"
            return JsonResponse({
                'status': 'success', 
                'message': f'Movie is now {status}',
                'is_hidden': movie.is_hidden
            })
            
        return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@staff_member_required
def supervisor_dashboard(request):
    """Supervisor Portal / Dashboard"""
    all_movies = Movie.objects.filter(is_hidden=True).order_by('-updated_at')
    
    # Add pagination
    paginator = Paginator(all_movies, 20)  # Show 20 movies per page
    page_number = request.GET.get('page', 1)
    movies = paginator.get_page(page_number)
    hidden_count = Movie.objects.filter(is_hidden=True).count()
    total_views = MovieView.objects.count()
    views_today = MovieView.objects.filter(viewed_at__date=timezone.now().date()).count()
    
    # Top 10 Viewed Movies
    top_movies = Movie.objects.annotate(
        view_count=Count('views')
    ).order_by('-view_count')[:10]
    
    # Recent Traffic (last 10 views)
    recent_traffic = MovieView.objects.select_related('movie', 'user').all()[:10]

    # Daily views for the last 7 days
    seven_days_ago = timezone.now().date() - timedelta(days=6)
    daily_stats = MovieView.objects.filter(
        viewed_at__date__gte=seven_days_ago
    ).values('viewed_at__date').annotate(count=Count('id')).order_by('viewed_at__date')

    # Prepare data for Chart.js
    chart_labels = []
    chart_data = []
    
    # Store stats in a dict with string keys for reliable lookup
    stats_dict = {}
    for s in daily_stats:
        date_key = s['viewed_at__date']
        if date_key:
            # Ensure the key is a string in YYYY-MM-DD format
            if not isinstance(date_key, str):
                date_key = date_key.strftime('%Y-%m-%d')
            stats_dict[date_key] = s['count']
    
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        chart_labels.append(date.strftime('%b %d'))
        # Lookup using the same string format
        chart_data.append(stats_dict.get(date.strftime('%Y-%m-%d'), 0))

    context = {
        'movies': movies,
        'hidden_count': hidden_count,
        'total_views': total_views,
        'views_today': views_today,
        'top_movies': top_movies,
        'recent_traffic': recent_traffic,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    
    return render(request, 'movies/supervisor_dashboard.html', context)
