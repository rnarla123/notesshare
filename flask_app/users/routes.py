from flask import Blueprint, redirect, url_for, render_template, flash, request, session
from flask_login import current_user, login_required, login_user, logout_user

from .. import bcrypt
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UploadNotesForm
from ..models import User, Notes
from ..utils import current_time

from werkzeug.utils import secure_filename
import pyotp
import qrcode
import qrcode.image.svg as svg
from io import BytesIO

users = Blueprint('users', __name__, static_folder='static', template_folder='templates')


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("notes.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        session['new_username'] = user.username
        user.save()

        return redirect(url_for("users.tfa"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("notes.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.upload"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("notes.index"))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    username_form = UpdateUsernameForm()

    if username_form.validate_on_submit():
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(url_for("users.account"))

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form,
    )

@users.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    notes_form = UploadNotesForm()

    if notes_form.submit_pic.data and notes_form.validate_on_submit():
        img = notes_form.file.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'

        notes = Notes(
            notetaker=current_user._get_current_object(),
            title=notes_form.title.data,
            class_name=notes_form.class_name.data,
            date=current_time()
        )
        notes.notes_file.put(img.stream, content_type=content_type)
        
        notes.save()

        return redirect(url_for('users.upload'))

    notes = Notes.objects(notetaker=current_user._get_current_object())

    return render_template(
        "upload.html",
        title="Account",
        notes_form=notes_form,
        notes=notes
    )


@users.route("/qr_code")
def qr_code():
    if 'new_username' not in session:
        return redirect(url_for('main.index'))
    
    user = User.objects(username=session['new_username']).first()
    session.pop('new_username')

    uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(name=user.username, issuer_name='CMSC388J-2FA')
    img = qrcode.make(uri, image_factory=svg.SvgPathImage)
    stream = BytesIO()
    img.save(stream)

    headers = {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return stream.getvalue(), headers


@users.route("/tfa")
def tfa():
    if 'new_username' not in session:
        return redirect(url_for('main.index'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers