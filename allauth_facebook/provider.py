from allauth.socialaccount.providers.facebook.provider import FacebookProvider
from allauth.account.models import EmailAddress


class FacebookVerifiedEmailProvider(FacebookProvider):

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email:
            # If there's an email address, facebook has verified it.
            # https://stackoverflow.com/questions/14280535/is-it-possible-to-check-if-an-email-is-confirmed-on-facebook
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [FacebookVerifiedEmailProvider]
