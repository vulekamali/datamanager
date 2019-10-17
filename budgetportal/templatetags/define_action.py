from django import template
from django.utils.safestring import mark_safe

import json
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name="jsonify")
def json_dumps(data):
    return json.dumps(data)


@register.assignment_tag
def assign(val=None):
    return val


@register.filter
def hash(h, key):
    if h:
        if key in h:
            return h[key]
    else:
        logger.warning(
            "Hash template tag received a null object for key {}".format(key)
        )
    return None
