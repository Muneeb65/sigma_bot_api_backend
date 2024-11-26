import json
from base64 import b64encode
from hashlib import sha1, sha256

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
# from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied

from apps.common.constants import (FRONTEND_VERIFY_EMAIL_PATH,)

from .mailer import Mailer
# from .models import WebRequest


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + user.password + str(user.email_verified) + str(timestamp)

def check_user_validity(user):
    if not user.email_verified:
        raise PermissionDenied(_('Please verify your email to login.'))
    if not user.is_active:
        raise PermissionDenied()
    if user.is_cabbies_user != settings.IS_CABBIES_PORTAL:
        portal_name = 'Cabbies' if settings.IS_CABBIES_PORTAL else 'PHC'
        raise PermissionDenied(_(f"User does not belong to {portal_name} Portal"))


def _unpadded_encode(data, encoder=b64encode):
    return encoder(data).rstrip(b'=').decode('ascii')


def hash_string(string, hasher=sha256, formatter=_unpadded_encode):
    return formatter(hasher(string.encode('utf-8')).digest())


def sha1_string(string, formatter=_unpadded_encode):
    return hash_string(string, hasher=sha1, formatter=formatter)


def map_resource_selection(model_name, fields):
    resource_selection = RESOURCE_SELECTION_MAPPING.get(model_name)
    if isinstance(resource_selection, dict):
        for key, value in resource_selection.items():
            if value.intersection(fields):
                resource_selection = key
                break
    return resource_selection


def dumps(value):
    return json.dumps(value, default=lambda o: None)


def save_request(request):
    meta = request.META.copy()
    meta.pop('QUERY_STRING', None)
    meta.pop('HTTP_COOKIE', None)
    remote_addr_fwd = None

    if 'HTTP_X_FORWARDED_FOR' in meta:
        remote_addr_fwd = meta['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
        if remote_addr_fwd == meta['HTTP_X_FORWARDED_FOR']:
            meta.pop('HTTP_X_FORWARDED_FOR')

    if request.method == 'POST':
        post_data = dumps(request.POST) + dumps(request.data)
    else:
        post_data = None

    WebRequest(
        host=request.get_host(),
        path=request.path,
        method=request.method,
        uri=request.build_absolute_uri(),
        user_agent=meta.pop('HTTP_USER_AGENT', None),
        remote_addr=meta.pop('REMOTE_ADDR', None),
        remote_addr_fwd=remote_addr_fwd,
        meta=None if not meta else dumps(meta),
        cookies=None if not request.COOKIES else dumps(request.COOKIES),
        get=None if not request.GET else dumps(request.GET),
        post=post_data,
    ).save()


def send_verification_email(user):
    context = get_verification_email_context(user)
    subject_template = "emails/verification_email_subject.txt"
    body_template = "emails/verification_email.html"
    to = [user.email]

    Mailer.send_email_with_template(
        subject_template=subject_template,
        body_template=body_template,
        context=context,
        to=to
    )


def get_verification_email_context(user):
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = AccountActivationTokenGenerator().make_token(user)
    relative_link = f'{FRONTEND_VERIFY_EMAIL_PATH}?uidb64={uidb64}&token={token}'
    verification_link = f'{settings.FRONTEND_URL}{relative_link}'

    return {
        'user': user,
        'verification_link': verification_link
    }
