from django.db import models


# This class represents an unsent email
class Email(models.Model):
    SUBJECT_MAX_LEN = 255

    datetime = models.DateTimeField(auto_now_add=True, verbose_name='date')
    subject = models.CharField(max_length=SUBJECT_MAX_LEN, verbose_name='sujet',)
    from_email = models.EmailField(verbose_name='adresse mail source',)
    body = models.TextField(verbose_name='contenu')


class DestAddr(models.Model):
    email = models.ForeignKey(Email, related_name='to')
    addr = models.EmailField(verbose_name='adresse mail',)


class Attachment(models.Model):
    FILENAME_MAX_LEN = 255
    MIMETYPE_MAX_LEN = 255

    email = models.ForeignKey(Email, related_name='attachments')
    filename = models.CharField(max_length=FILENAME_MAX_LEN, verbose_name='nom',)
    mimetype = models.CharField(max_length=MIMETYPE_MAX_LEN, verbose_name='mimetype',)
    content = models.TextField(verbose_name='contenu',)
