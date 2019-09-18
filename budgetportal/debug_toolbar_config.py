from django.conf import settings


def show_toolbar_check(request):
    return settings.DEBUG and settings.DEBUG_TOOLBAR
