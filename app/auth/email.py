from flask import render_template, current_app
from app.email import send_email
import os
from config import Config

def send_password_reset_email(user):
    '''
    Sends a password reset email.

    :param user:        A user object.
    '''
    token = user.get_reset_password()
    send_email('Reset your password',
               sender='{}'.format(Config.MAIL_USERNAME),
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_verify_email_email(user):
    '''
    Sends a email verification email.

    :param user:        A user object.
    '''
    token = user.get_verify_email()
    send_email(
        'Verify your email',
        sender='{}'.format(Config.MAIL_USERNAME),
        recipients=[user.email],
        text_body=render_template('email/verify_email.txt', user=user, token=token),
        html_body=render_template('email/verify_email.html', user=user, token=token))