from flask import redirect, url_for
from flask_login import current_user

def check_logged_in():
    '''
    If the current user is logged in, it redirects them to their dashboard.
    '''
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))