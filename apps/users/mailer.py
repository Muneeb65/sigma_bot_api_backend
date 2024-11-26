from apps.common.utils import get_site_url
import logging
import os
from config import settings

from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from django.template.loader import render_to_string
from premailer import premailer

logger = logging.getLogger(__name__)


class Mailer:

    @classmethod
    def embed_images(cls, email_message, embed_images):
        if embed_images:
            for path in embed_images:
                filename = os.path.basename(path)
                attachment = MIMEImage(open(path, 'rb').read())
                attachment.add_header('Content-ID', '<%s>' % filename)
                attachment.add_header('Content-ID', '<%s>' % filename)
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                email_message.attach(attachment)
                email_message.mixed_subtype = 'related'
        return email_message

    @classmethod
    def send_email(cls, subject, body, from_email=None, to=None, bcc=None, cc=None, attachments=None,
                   embed_images=None, reply_to=None, connection=None, headers=None):
        env_name = settings.ENV_NAME
        if env_name != 'PRODUCTION':
            subject = '{} - {}'.format(env_name, subject)

        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        print("(((((((((((((((((((((((((((((())))))))))))))))))))))))))))))")

        print(from_email
        )
        # if settings.DISABLE_EXTERNAL_MESSAGES:
        #     to = settings.CONTACT_EMAILS
        #     cc = list()
        #     bcc = list()

        email_message = EmailMessage(subject, body, from_email, to, bcc, connection, None, headers, cc, reply_to)
        email_message = cls.embed_images(email_message, embed_images)

        if attachments:
            for path in attachments:
                email_message.attach_file(path)

        email_message.content_subtype = 'html'

        try:
            send_status = email_message.send()
            return send_status
        except Exception:
            raise

    @classmethod
    def send_email_with_template(cls, subject_template, body_template, context, from_email=None, to=None, bcc=None,
                                 cc=None, attachments=None, embed_images=None, reply_to=None, connection=None,
                                 headers=None):
        pre_mailer = premailer.Premailer()
        context['site_host'] = get_site_url
        context['is_cabbies_portal'] = True
        subject = loader.render_to_string(subject_template, context)
        subject = ''.join(subject.splitlines())
        body = render_to_string(body_template, context)
        # body = pre_mailer.transform(body)

        return cls.send_email(subject, body, from_email=from_email, to=to, bcc=bcc, cc=cc,
                              attachments=attachments, embed_images=embed_images, reply_to=reply_to,
                              connection=connection, headers=headers)
