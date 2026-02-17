from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Aura!')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please check the form.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def supervisor_login(request):
    """Supervisor login"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('supervisor_dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f'Supervisor {username} logged in successfully!')
                    return redirect('supervisor_dashboard')
                else:
                    messages.error(request, 'Access denied. Only supervisors can access this portal.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/supervisor_login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    """User profile page"""
    if request.user.is_staff:
        messages.info(request, "As a Supervisor, your primary interface is the Portal Dashboard.")
        return redirect('supervisor_dashboard')
        
    from movies.models import Watchlist, Rating
    
    watchlist_count = Watchlist.objects.filter(user=request.user).count()
    ratings_count = Rating.objects.filter(user=request.user).count()
    recent_ratings = Rating.objects.filter(user=request.user).select_related('movie')[:5]
    
    context = {
        'watchlist_count': watchlist_count,
        'ratings_count': ratings_count,
        'recent_ratings': recent_ratings,
    }
    
    return render(request, 'accounts/profile.html', context)
