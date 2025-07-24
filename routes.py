import string
import random
from flask import request, flash, redirect, url_for, render_template, send_file
from forms import RegisterForm, LoginForm, ProfileForm
from models import User
from ext import app, db
from models import URL
from flask_login import login_user, logout_user, current_user, login_required
import os
import qrcode
from io import BytesIO
import base64


@app.route("/qr/<short_code>")
def generate_qr(short_code):
    short_url = request.host_url + short_code
    img = qrcode.make(short_url)

    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return render_template("qr.html", qr_code=qr_b64, short_url=short_url)


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = "".join(random.choices(characters, k=length))
        if not URL.query.filter_by(short_url=short_code).first():
            return short_code


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["original_url"]

        if not original_url.startswith("http://") and not original_url.startswith("https://"):
            flash("Please enter a link starting with http:// or https://", "error")
            return redirect(url_for("index"))

        short_code = generate_short_code()

        if current_user.is_authenticated:
            new_url = URL(original_url=original_url, short_url=short_code, user_id=current_user.id)
        else:
            new_url = URL(original_url=original_url, short_url=short_code)

        db.session.add(new_url)
        db.session.commit()

        short_url = request.host_url + short_code
        return render_template("index.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<short_code>")
def redirect_to_original(short_code):
    url = URL.query.filter_by(short_url=short_code).first()
    if url:
        return redirect(url.original_url)
    else:
        return "URL not found", 404


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_username = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_username:
            flash("Username is already in use.", "danger")
            return redirect("/register")
        if existing_email:
            flash("Email is already in use.", "danger")
            return redirect("/register")
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        image = form.profile_image.data
        if image:
            filename = image.filename
            directory = os.path.join(app.root_path, "static", "images", filename)
            image.save(directory)
            user.img = filename
        else:
            user.img = "default.png"

        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect("/login")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("Username does not exist.", "danger")
        elif not user.check_password(form.password.data):
            flash("Incorrect password.", "danger")
            return redirect("/")
        else:
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect("/")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.profile_image.data:
            image = form.profile_image.data
            filename = image.filename
            directory = os.path.join(app.root_path, "static", "images", image.filename)
            image.save(directory)
            current_user.img = filename
        db.session.commit()
        return redirect("/profile")

    form.username.data = current_user.username
    form.email.data = current_user.email

    user_links = URL.query.filter_by(user_id=current_user.id).all()

    return render_template("profile.html", form=form, user_links=user_links)


@app.route("/delete_link/<int:link_id>", methods=["POST"])
@login_required
def delete_link(link_id):
    link = URL.query.get(link_id)
    db.session.delete(link)
    db.session.commit()
    flash("Link deleted successfully.", "success")
    return redirect(url_for('profile'))


@app.route('/delete_account', methods=["POST"])
@login_required
def delete_account():
    user = User.query.get(current_user.id)

    db.session.delete(user)
    db.session.commit()
    logout_user()

    flash("Your account has been deleted.", "success")
    return redirect("/")


@app.route("/admin/users")
@login_required
def admin_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)


@app.route("/user/<int:user_id>")
@login_required
def view_user(user_id):
    user = User.query.get(user_id)
    return render_template("user_profile.html", user=user)


@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()
    flash("User and all their posts and comments deleted.", "success")
    return redirect(url_for('admin_users'))


@app.route("/about")
def about():
    return render_template("about.html")
