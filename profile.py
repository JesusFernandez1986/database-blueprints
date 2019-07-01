from flask import Blueprint, request, render_template, redirect, url_for
import hashlib
from models import User, db

profiles = Blueprint("bp_profile", __name__)


@profiles.route("/profile")
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("bp_main.index"))



@profiles.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return render_template("edit_profile.html", user=user)
    elif request.method == "POST":
        name = request.form.get("profile-name")     #cogemos el nombre y el email del formulario y lo guardamos en estas variables
        email = request.form.get("profile-email")
        new_password = request.form.get("new_password")

        if len(new_password) > 6:
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            if hashed_new_password != user.password:
                user.password = hashed_new_password
            else:
                message1 = "This password is the same than the old one, please set a different one"
                return render_template("edit_profile.html", message1=message1, user=user)
        else:
            message2 = "Your password must be at least 6 characters long"
            return render_template("edit_profile.html", message2=message2, user=user)

        user.name = name    #asignamos el valor de la variable name y email a la propiedad user.name y user.email del objeto
        user.email = email
        db.add(user)                #guardamos los cambios en la base de datos
        db.commit()

        return redirect(url_for("bp_profile.profile"))


@profiles.route("/delete", methods=["GET", "POST"])
def delete():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return render_template("delete.html", user=user)
    elif request.method == "POST":
        if not user.is_active:
            message3 = "Su perfil ha sido desactivado correctamente"
            user.is_active = False
            db.add(user)
            db.commit()
            resp = make_response(render_template("edit_profile.html", message3=message3))
            resp.set_cookie('session_token', expires=0)
            return resp
        else:
            return redirect(url_for("bp_profile.profile"))
