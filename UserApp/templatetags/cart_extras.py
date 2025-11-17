from django import template

register = template.Library()

@register.filter
def multiply(price, quantity):
    try:
        return price * quantity
    except:
        return 0
