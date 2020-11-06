from app.main import bp
from flask_login import current_user, login_required
from flask import render_template
from app.auth.email import send_verify_email_email
from config import Config

@bp.route('/')
@bp.route('/home')
def home():
    return render_template('main/home.html', title='Welcome!')


@bp.route('/dashboard')
@login_required
def dashboard():
    if Config.MAIL_SERVER is not None and Config.MAIL_PORT is not None:
        if current_user.is_verified is False:
            send_verify_email_email(current_user)

    return render_template('main/dashboard.html', title='Your dashboard')