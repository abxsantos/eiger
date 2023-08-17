from django import template

register = template.Library()


@register.filter(name='add_css')
def add_css_class(value, css_class):
    """Add a CSS class to a component."""
    return value.as_widget(attrs={'class': css_class})
