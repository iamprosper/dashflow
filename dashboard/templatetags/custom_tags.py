from django import template

register = template.Library()

@register.filter
def custom_range(start, stop, step=1):
    try:
        start, stop, step = int(start), int(stop), int(step)
        return range(start, stop, step)
    except (ValueError, TypeError):
        return []