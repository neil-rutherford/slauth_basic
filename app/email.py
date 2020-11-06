from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, message):
    '''
    Helper function that sends an email.

    :param app:             The Flask app object.
    :param message:         The Flask-Mail message object.
    '''
    with app.app_context():
        mail.send(message)


def send_email(subject, sender, recipients, text_body, html_body):
    '''
    Sends an email asynchronously, meaning that it doesn't slow down the app as much as it normally would.

    :param subject:         The subject of the email, as a string.
    :param sender:          The sending email address, as a string.
    :param recipients:      The intended recipients of the email, as a list of strings.
    :param text_body:       The email body, as a plaintext document.
    :param html_body:       The email body, as an HTML document.
    '''
    message = Message(subject, sender=sender, recipients=recipients)
    message.body = text_body
    message.html = html_body
    Thread(target=send_async_email,args=(current_app._get_current_object(), message)).start()