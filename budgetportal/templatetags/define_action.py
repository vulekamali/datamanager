from django import template
register = template.Library()

@register.assignment_tag
def assign(val=None):
  return val

@register.filter
def hash(h, key):
  if key in h:
    return h[key]
  return None