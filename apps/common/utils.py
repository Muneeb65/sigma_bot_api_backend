import uuid
from datetime import date, datetime

from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

# from apps.common.constants import DEVELOPMENT, LOCAL, RELEASE
# from apps.common.validators import (emergency_contact_validator,
#                                     phone_validator_pakistan,
#                                     phone_validator_singapore)
from config import settings


def get_phone_number_validators(emergency_contact=False):
    validators = list()
    if settings.ENV_NAME in [LOCAL, DEVELOPMENT, RELEASE]:
        validators.append(phone_validator_pakistan)
    else:
        if emergency_contact:
            validators.append(emergency_contact_validator)
        else:
            validators.append(phone_validator_singapore)
    return validators


def get_country_code():
    country_code = '+65'
    if settings.ENV_NAME in [LOCAL, DEVELOPMENT, RELEASE]:
        country_code = '+92'
    return country_code


def user_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), extension)
    uidb64 = urlsafe_base64_encode(smart_bytes(instance.user.id))
    return f'user_{uidb64}/{filename}'


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def get_site_url():
    return settings.BACKEND_URL


def query_param_to_boolean(value):
    boolean_value = None
    if value in ('true', 'True'):
        boolean_value = True
    elif value in ('false', 'False'):
        boolean_value = False
    return boolean_value


def sting_to_date(date_string, formats):
    for format in formats:
        try:
            return datetime.strptime(date_string, format)
        except ValueError:
            continue
    raise ValueError('no valid date format found')
