from django.db import models
from django.core.mail import EmailMessage


# This class represents an unsent email
class Email(models.Model):
    SUBJECT_MAX_LEN = 255

    datetime = models.DateTimeField(auto_now_add=True, verbose_name='date')
    subject = models.CharField(max_length=SUBJECT_MAX_LEN, verbose_name='sujet',)
    from_email = models.EmailField(verbose_name='adresse mail source',)
    body = models.TextField(verbose_name='contenu')

    def to_message(self):
        msg = EmailMessage(
            self.subject,
            self.body,
            self.from_email,
            [str(dest) for dest in self.to.all()],
            [],
        )

        for attachment in self.attachments.all():
            msg.attach(*attachment.to_tuple())

        return msg


class DestAddr(models.Model):
    email = models.ForeignKey(Email, related_name='to')
    addr = models.EmailField(verbose_name='adresse mail',)

    def __str__(self):
        return self.addr


class Attachment(models.Model):
    FILENAME_MAX_LEN = 255
    MIMETYPE_MAX_LEN = 255

    email = models.ForeignKey(Email, related_name='attachments')
    filename = models.CharField(max_length=FILENAME_MAX_LEN, verbose_name='nom',)
    mimetype = models.CharField(max_length=MIMETYPE_MAX_LEN, verbose_name='mimetype',)
    content = models.TextField(verbose_name='contenu',)

    def to_tuple(self):
        return self.filename, self.content, self.mimetype
