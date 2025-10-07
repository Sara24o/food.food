from django import template

register = template.Library()


@register.filter(name="length_is")
def length_is(value, arg):
    """
    Compatibility shim for the removed Django template filter `length_is`.
    Returns True if len(value) == int(arg), else False.
    """
    try:
        length = len(value)
    except Exception:
        return False

    try:
        expected_length = int(arg)
    except (TypeError, ValueError):
        return False

    return length == expected_length


