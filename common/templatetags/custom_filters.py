from django import template

register = template.Library()

def lookup(d, key):
    try:
        if key in d:
            return d[key]
        else:
            return None
    except:
        return None
    
register.filter(lookup)
