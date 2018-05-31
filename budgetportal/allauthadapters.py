from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from urllib import urlencode


class AccountAdapter(DefaultAccountAdapter):
    """
    Add redirect URL to verification link so that users continue
    where they were headed after authentication.
    """
    def get_email_confirmation_url(self, request, emailconfirmation):
        print
        print "###"
        print request.url
        print "POST %r" % request.POST
        print "GET %r" % request.GET
        print "###"
        print
        next_url = request.POST.get('next')
        email_conf_url = super(AccountAdapter, self).get_email_confirmation_url(request, emailconfirmation)
        if next_url:
            return '%s?%s' % (email_conf_url, urlencode({'next': next_url}))
        else:
            return email_conf_url

    def get_email_confirmation_redirect_url(self, request):
        """
        Used during email confirmation.
        Gets the URL to send them after confirmation from the request URL
        """
        next_url = request.GET.get('next')
        if next_url:
            return next_url
        else:
            return super(AccountAdapter, self).get_email_confirmation_redirect_url(request)


# https://stackoverflow.com/questions/19354009/django-allauth-social-login-automatically-linking-social-site-profiles-using-th
class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        We're trying to solve different use cases:
        - social account already exists, just go on
        - social account has no email or email is unknown, just go on
        - social account's email exists, link social account to existing user
        """

        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email = sociallogin.account.extra_data['email'].lower()
            email_address = EmailAddress.objects.get(email__iexact=email)

        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            return

        # if it does, connect this new social login to the existing user
        user = email_address.user
        sociallogin.connect(request, user)
