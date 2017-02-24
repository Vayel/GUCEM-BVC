from smtplib import SMTPException

from django.core.mail.backends import smtp

from .. import models


class EmailBackend(smtp.EmailBackend):

    def save_mail(self, msg):
        email = models.Email(
            subject=msg.subject,
            from_email=msg.from_email,
            body=msg.body,
        )
        email.save()

        for addr in msg.to:
            models.email.DestAddr.objects.create(email=email, addr=addr).save()

        for attachment in msg.attachments:
            models.email.Attachment(
                email=email,
                filename=attachment[0],
                mimetype=attachment[2],
                content=attachment[1],
            ).save()


    def send_messages(self, email_messages):
        sent = 0

        for msg in email_messages:
            try:
                n = super().send_messages([msg])
            except SMTPException:
                self.save_mail(msg)
            else:
                sent += n
                if not n:
                    self.save_mail(msg)
            
        return sent
