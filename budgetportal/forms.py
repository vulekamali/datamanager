"""
https://stackoverflow.com/questions/22665211/is-there-any-solutions-to-add-captcha-to-django-allauth
"""

from django import forms
from captcha.fields import ReCaptchaField


class AllauthSignupForm(forms.Form):

    captcha = ReCaptchaField()

    def signup(self, request, user):
        """ Required, or else it throws deprecation warnings """
        pass
