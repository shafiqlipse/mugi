from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get a key from a dict in templates"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
