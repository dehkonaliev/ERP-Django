import re
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return value from dictionary by key."""
    return dictionary.get(key)


@register.filter
def youtube_embed(value):
    """Take a YouTube URL or video id and return embeddable URL."""
    if not value:
        return ''
    if 'youtube.com' in value or 'youtu.be' in value:
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',
            r'youtube\.com/embed/([\w-]+)',
            r'youtu\.be/([\w-]+)',
        ]
        for p in patterns:
            m = re.search(p, value)
            if m:
                return 'https://www.youtube.com/embed/' + m.group(1)
    return 'https://www.youtube.com/embed/' + value