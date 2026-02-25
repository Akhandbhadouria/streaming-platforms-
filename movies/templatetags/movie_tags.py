from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Return dictionary[key], or None if key is not present."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
