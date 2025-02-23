import random
import smtplib
from django.core.mail import send_mail
from django.conf import settings

def generate_otp_code(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_otp_email(user_email, otp_code):
    subject = "Your 2FA Code for Connectly"
    message = f"Hello,\n\nYour One-Time Password (OTP) is: {otp_code}\n\n" \
              f"Use this code to complete your login.\n\nThanks!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
