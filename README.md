# Aura Platform

A modern, responsive movie streaming platform built with Django, featuring TMDB (The Movie Database) integration for movie data and YouTube API for trailers.

## Features

- **Movie Discovery**: Browse popular, trending, top-rated, upcoming, and now playing movies.
- **Search**: Find movies by title using TMDB's powerful search API.
- **Detailed Info**: View movie details including rating, runtime, genres, cast, and similar movies.
- **Trailers**: Watch official trailers via YouTube integration.
- **User Accounts**: Secure registration and login system.
- **Watchlist**: Save movies to your personal watchlist.
- **Ratings & Reviews**: Rate movies and write reviews.
- **Modern UI**: Netflix-inspired dark theme with responsive design for all devices.

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (Development)
- **External APIs**: 
  - TMDB API (Movie Data)
  - YouTube Data API (Trailers)
- **Frontend**: HTML5, CSS3 (Custom), JavaScript

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install django requests pillow python-dotenv
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the project root with the following keys:
   ```
   TMDB_API_KEY=your_tmdb_api_key
   TMDB_ACCESS_TOKEN=your_tmdb_access_token
   YOUTUBE_API_KEY=your_youtube_api_key
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run Server**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000/`

## Project Structure

- `Aura/`: Main project configuration
- `movies/`: Core app handling movie data, API integration, and views
- `accounts/`: User authentication and profile management
- `templates/`: HTML templates for all pages
- `static/`: CSS, JavaScript, and image assets

## API Usage

This project uses the TMDB API but is not endorsed or certified by TMDB.
This project uses the YouTube Data API.
