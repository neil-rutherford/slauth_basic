from app import db
from app.models import User
from flask import redirect, render_template, url_for, flash, request
from app.auth import bp
from flask_login import login_user, current_user, logout_user
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.utils import check_logged_in

@bp.route('/register', methods=['GET', 'POST'])
def register():
    check_logged_in()
    
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(email=str(form.email.data))
        user.first_name = str(form.first_name.data)
        user.last_name = str(form.last_name.data)
        user.set_password(str(form.password.data))
        user.is_verified = False
        user.email_opt_in = bool(form.email_opt_in.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html', title='Register as a new user!', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    check_logged_in()

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=str(form.email.data)).first()
        if user is None or not user.check_password(str(form.password.data)):
            flash('Invalid email or password.', category='error')
            return redirect(url_for('auth.login'))
        login_user(user=user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Log in', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    check_logged_in()
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password.', category='message')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset password', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    check_logged_in()
    
    user = User.verify_reset_password_token(token)
    if not user:
        make_sentry(user_id=None, domain_id=None, ip_address=request.remote_addr, endpoint='auth.reset_token', status_code=404, status_message='User not found')
        return redirect(url_for('promo.home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', category='message')
        make_sentry(user_id=None, domain_id=None, ip_address=request.remote_addr, endpoint='auth.reset_token', status_code=200, status_message='OK')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.verify_verify_email_token(token)
    if not user:
        return redirect(url_for('main.home'))
    else:
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        flash("Your email has been verified.", category='message')
        return redirect(url_for('main.dashboard'))