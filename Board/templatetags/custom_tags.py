from django import template

register = template.Library()

@register.filter
def Active_User(user):
    return user.groups.filter(name='Active').exists()

@register.filter
def Viewer_User(user):
    return user.groups.filter(name='Viewer').exists()

@register.filter
def Host_User(user):
    return user.groups.filter(name='Host').exists()