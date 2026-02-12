from django import template

register = template.Library()

@register.filter
def first_last_name(value):
    words = str(value).split()
    if len(words) > 1:
        return f"{words[0]} {words[-1]}"
    return value  # In case there's only one word or an empty string


@register.filter
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()