from django import template
from accounts.models import UserProfile

register = template.Library()

@register.simple_tag
def get_user_avatar(user):
    if user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=user)
            if profile.avatar:
                return profile.avatar.url
        except UserProfile.DoesNotExist:
            pass
    return None
