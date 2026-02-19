from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AvatarUploadForm, ProfileEditForm
from .models import UserProfile, EmailOTP


def register(request):
    """User registration with OTP email verification"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until OTP verified
            user.save()
            
            # Generate and send OTP
            otp_code = EmailOTP.generate_otp()
            EmailOTP.objects.create(user=user, otp=otp_code)
            
            try:
                send_mail(
                    subject='Aura - Verify Your Email',
                    message=f'Your verification code is: {otp_code}\n\nThis code expires in 10 minutes.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except BaseException as e:
                # Catch ALL exceptions including SystemExit from gunicorn worker timeouts
                import logging
                logging.getLogger(__name__).error(f"Failed to send OTP email: {type(e).__name__}: {e}")
            
            request.session['otp_user_id'] = user.id
            messages.success(request, 'Account created! Check your email for the verification code.')
            return redirect('verify_otp')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def verify_otp(request):
    """Verify email OTP"""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'No pending verification. Please register first.')
        return redirect('register')
    
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('register')

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()
        
        latest_otp = EmailOTP.objects.filter(user=user, is_verified=False).order_by('-created_at').first()
        
        if not latest_otp:
            messages.error(request, 'No OTP found. Please request a new one.')
        elif latest_otp.is_expired():
            messages.error(request, 'OTP has expired. Please request a new one.')
        elif latest_otp.otp == otp_input:
            latest_otp.is_verified = True
            latest_otp.save()
            user.is_active = True
            user.save()
            del request.session['otp_user_id']
            login(request, user)
            messages.success(request, 'Email verified! Welcome to Aura!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'email': user.email})


def resend_otp(request):
    """Resend OTP email"""
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('register')
    
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('register')
    
    # Invalidate old OTPs
    EmailOTP.objects.filter(user=user, is_verified=False).delete()
    
    otp_code = EmailOTP.generate_otp()
    EmailOTP.objects.create(user=user, otp=otp_code)
    
    try:
        send_mail(
            subject='Aura - Verify Your Email',
            message=f'Your new verification code is: {otp_code}\n\nThis code expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(request, 'A new OTP has been sent to your email.')
    except Exception:
        messages.error(request, 'Failed to send email. Please try again.')

    return redirect('verify_otp')


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
