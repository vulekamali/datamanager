# https://meta.discourse.org/t/sso-example-for-django/14258

import base64
import hmac
import hashlib
import urllib.request
import urllib.parse
import urllib.error

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings

from urllib.parse import parse_qs

from allauth.account.decorators import verified_email_required


@verified_email_required
def sso(request, client_id):
    payload = request.GET.get("sso")
    signature = request.GET.get("sig")

    if payload is None or signature is None:
        return HttpResponseBadRequest(
            "No SSO payload or signature. Please contact support if this problem persists."
        )

    # Validate the payload

    try:
        payload_bytes = urllib.parse.unquote(payload).encode()
        decoded = base64.decodebytes(payload_bytes)
        assert b"nonce" in decoded
        assert len(payload_bytes) > 0
    except AssertionError:
        return HttpResponseBadRequest(
            "Invalid payload. Please contact support if this problem persists."
        )

    key = settings.DISCOURSE_SSO_SECRET  # must not be unicode
    h = hmac.new(key.encode(), payload_bytes, digestmod=hashlib.sha256)
    this_signature = str(h.hexdigest())

    if not hmac.compare_digest(this_signature, signature):
        return HttpResponseBadRequest(
            "Invalid payload. Please contact support if this problem persists."
        )

    ## Build the return payload

    qs = parse_qs(decoded.decode())
    params = {
        "nonce": qs["nonce"][0],
        "email": request.user.email,
        "external_id": request.user.id,
        "username": request.user.username,
        "name": request.user.get_full_name(),
    }
    payload_string = urllib.parse.urlencode(params)
    return_payload = base64.encodebytes(payload_string.encode())
    h = hmac.new(key.encode(), return_payload, digestmod=hashlib.sha256)
    query_string = urllib.parse.urlencode({"sso": return_payload, "sig": h.hexdigest()})

    # Redirect back to Discourse

    url = settings.DISCOURSE_SSO_URLS[client_id]

    return HttpResponseRedirect("%s?%s" % (url, query_string))
