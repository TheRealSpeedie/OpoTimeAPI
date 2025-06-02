from django.core.mail import send_mail
from django.conf import settings

def send_invitation_email(invitation):
    link = f"{settings.FRONTEND_URL}/invitations/confirm/{invitation.token}"
    subject = "Du wurdest zu einem Projekt eingeladen"
    message = f"Hallo,\n\nDu wurdest zu einem Projekt eingeladen.\nKlicke hier, um beizutreten:\n{link}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [invitation.to_user.email],
        fail_silently=False,
    )
