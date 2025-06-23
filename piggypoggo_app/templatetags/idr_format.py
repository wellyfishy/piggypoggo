from django import template

register = template.Library()

@register.filter
def idr(value):
    try:
        num = int(value)
        return f"{num:,.0f}".replace(",", ".")
    except:
        return value