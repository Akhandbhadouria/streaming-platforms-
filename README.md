# Aura Platform

A modern, responsive movie streaming platform built with Django, featuring TMDB (The Movie Database) integration for movie data and YouTube API for trailers.

## Features

- **Movie Discovery**: Browse popular, trending, top-rated, upcoming, and now playing movies.
- **Search**: Find movies by title using TMDB's powerful search API.
- **Detailed Info**: View movie details including rating, runtime, genres, cast, and similar movies.
- **Trailers**: Watch official trailers via YouTube integration.
- **User Accounts**: Secure registration and login system with email validation.
- **Watchlist**: Save movies to your personal watchlist.
- **Ratings & Reviews**: Rate movies (1-10) and write reviews with validation.
- **Supervisor Portal**: Admin dashboard with analytics, view tracking, and content moderation.
- **Modern UI**: Netflix-inspired dark theme with responsive design for all devices.

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (Development)
- **External APIs**: 
  - TMDB API (Movie Data)
  - YouTube Data API v3 (Trailers)
- **Frontend**: HTML5, CSS3 (Custom), JavaScript, Font Awesome icons

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- TMDB API Account
- Google Cloud Project (for YouTube API)

## Setup Instructions

### 1. Clone the Repository (if applicable)
```bash
cd /path/to/streaming-platforms-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Main dependencies:
- `django` - Web framework
- `requests` - HTTP library for API calls
- `pillow` - Image processing
- `python-dotenv` - Environment variable management

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

#### Get TMDB API Key:
1. Create a free account at [TMDB](https://www.themoviedb.org/signup)
2. Go to Settings → API
3. Request an API key (choose "Developer" option)
4. Copy both the **API Key (v3 auth)** and **API Read Access Token**

#### Get YouTube API Key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **YouTube Data API v3**
4. Go to Credentials → Create Credentials → API Key
5. Copy the API key

Your `.env` should look like:
```env
TMDB_API_KEY=your_actual_tmdb_api_key
TMDB_ACCESS_TOKEN=your_actual_tmdb_access_token
YOUTUBE_API_KEY=your_actual_youtube_api_key
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Run Database Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 5. Create Superuser (for Admin Access)
```bash
python3 manage.py createsuperuser
```

Follow the prompts to create an admin account. This account will have access to the Supervisor Portal.

### 6. Run Development Server
```bash
python3 manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## Project Structure

```
streaming-platforms-/
├── Aura/                   # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── movies/                 # Core app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── services.py         # API service classes
│   ├── forms.py            # Custom forms
│   └── admin.py            # Admin panel configuration
├── accounts/               # User authentication
│   ├── views.py            # Login, registration views
│   └── forms.py            # Custom user forms
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── movies/             # Movie templates
│   └── accounts/           # Account templates
├── static/                 # Static files
│   └── css/style.css       # Custom styles
├── .env                    # Environment variables (not in git)
├── .env.example            # Example environment file
└── requirements.txt        # Python dependencies
```

## Usage

### Regular Users
1. **Register**: Create a new account at `/accounts/register/`
2. **Browse**: Explore movies by category (Popular, Trending, Top Rated, etc.)
3. **Search**: Find specific movies using the search bar
4. **Watch Trailers**: Click on any movie to view details and trailers
5. **Manage Watchlist**: Add/remove movies from your personal watchlist
6. **Rate & Review**: Submit ratings (1-10) and reviews for movies

### Supervisors (Admin Users)
1. **Access Portal**: Login at `/accounts/supervisor-login/`
2. **View Analytics**: See viewing statistics and popular movies
3. **Manage Content**: Hide/unhide movies for content moderation
4. **Track Traffic**: Monitor recent views and user activity

## API Usage

This project uses:
- **TMDB API** for movie data (not endorsed or certified by TMDB)
- **YouTube Data API** for trailer embeds

**API Rate Limits:**
- TMDB: 40 requests per 10 seconds
- YouTube: 10,000 units per day (default quota)

## Troubleshooting

### Movies Not Loading
- Verify TMDB API keys in `.env`
- Check Django logs for API errors
- Ensure internet connection is active

### Trailers Not Playing
- Verify YouTube API key in `.env`
- Check browser console for errors
- Some trailers may not be embeddable

### Admin Panel Access
- Create superuser: `python3 manage.py createsuperuser`
- Access at: `http://127.0.0.1:8000/admin/`
- Use supervisor login for portal: `/accounts/supervisor-login/`

### Database Issues
- Run migrations: `python3 manage.py migrate`
- Reset database: Delete `db.sqlite3` and run migrations again

## Security Notes

- **Never commit `.env` file** to version control
- Use strong `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS` for deployment
- Change default API keys before deployment

## License

This project is for educational purposes.

