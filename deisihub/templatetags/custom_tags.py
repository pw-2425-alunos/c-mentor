# app/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter
def get_previous_item(list, index):
    """Returns the previous item in the list based on the current index."""
    if index > 0:
        return list[index - 1]
    return None