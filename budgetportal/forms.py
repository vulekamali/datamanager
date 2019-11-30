"""
https://stackoverflow.com/questions/22665211/is-there-any-solutions-to-add-captcha-to-django-allauth
"""

from captcha.fields import ReCaptchaField
from django import forms


class AllauthSignupForm(forms.Form):

    captcha = ReCaptchaField()

    def signup(self, request, user):
        """ Required, or else it throws deprecation warnings """
        pass
