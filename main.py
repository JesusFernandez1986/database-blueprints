from flask import Flask, render_template, request, redirect, url_for, make_response, Blueprint
    from flask_login import LoginManager, login_user
    from models import User, db
    import random
    import hashlib
    import uuid

    app = Flask(__name__)
    app.secret_key = "1234567890"
    main = Blueprint("bp_main", __name__)

    from profile import profiles

    app.register_blueprint(profiles)
    db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "app.login"
    login_manager.init_app(app)


    wrong_guess = []




    @app.route("/login", methods=["POST"])
    def login():
        name = request.form.get("user-name")        #cogemos del formulario el nombre y el email y los guardamos en las variables name y email
        email = request.form.get("user-email")
        secret_number = random.randint(1, 30)       #generamos un numero aleatorio y lo guardamos en secret_number
        password = request.form.get("user-password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()     #encriptamos el password


        user = db.query(User).filter_by(email=email).first()    #comprobamos si ese usuario existe en nuestra base de datos, filtrando por el email

        if not user:                                #si no hay un usuario registrado, creamos una instancia nueva para ese usuario y la guardamos en la bsae de datos
            user = User(name=name, email=email, secret_number=secret_number, password=hashed_password,)
            db.add(user)
            db.commit()

        if hashed_password != user.password:
            return redirect(url_for("index"))
        else:             #si el password introducido es igual al de la base de datos generamos un numero de sesion y lo guardamos en la BD
            session_token = str(uuid.uuid4())
            user.session_token = session_token
            db.add(user)
            db.commit()

            response = make_response(redirect(url_for('bp_main.index')))
            response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')       #guardamos el token de sesions en una cookie llamada session_token

            login_user(user)
            return response

    @main.route('/', methods=["GET", "POST"])
    def index():
        if request.method == "GET":
            data = {}
            session_token = request.cookies.get("session")                        #guardamos el valor de la cookie session token en la variable session_token

            if session_token:
                user = db.query(User).filter_by(session_token=session_token).first()  #si tenemos una session token, miramos y comparamos en la base de datos
            else:                                                                       #si no creamos una instancia user vacia
                user = None

            data.update({'user': user})
            return render_template("index.html", data=data)


        elif request.method == "POST":
            guess = request.form.get('guess', False)
            session_token = request.cookies.get("session_token")
            user = db.query(User).filter_by(session_token=session_token).first()

            try:                    # compara si el valor introducido es un entero y si no lo es devuelve un error
                guess = int(guess)
            except Exception:
                data = {'result': False,
                        "user": user,
                        "error": 2}
                response = make_response(render_template("index.html", data=data))
                return response

            if guess > 30 or guess < 1:    #comprueba que ademas de ser un entero sea un valor comprendido entre 1 y 30, si no devuelve un error
                data = {'result': False,
                        "user": user,
                        "error": 1}
                response = make_response(render_template("index.html", data=data))
                return response

            if guess == int(user.secret_number):    # Si ha acertado:
                new_secret = random.randint(1, 30)
                user.secret_number = new_secret
                db.add(user)
                db.commit()
                new_wrong = wrong_guess.copy()
                data = {'result': True,
                        "wrong_guess": new_wrong,
                        "user": user}
                wrong_guess.clear()
                response = make_response(render_template("index.html", data=data))
                return response
            else:                              # Si no hemos acertado damos una pista para que pueda acertar
                if int(user.secret_number) < guess:
                    data = {'result': False, # Diferentes lineas para mas orden y solo un diccionario con datos
                            'hint': "Demasiado grande, prueba algo mas pequeño",
                            'user': user}
                else:
                    data = {'result': False,
                            'hint': "Demasiado pequeño, prueba algo mas grande",
                            'user': user}
                response = make_response(render_template("index.html", data=data))
                wrong_guess.append(guess)
            return response     # Devolvemos  un response por pantalla,mostrando un mensaje segun si ha acertado o si ha puesto un numero mayor o menor
        return render_template("index.html")

    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))


    @app.route("/users_list", methods=["GET"])
    @login_required
    def users_list():
        users = db.query(User).all()
        return render_template("users.html", users=users)


    @app.route("/user/<user_id>", methods=["GET"])
    @login_required
    def user_details(user_id):
        user = db.query(User).get(int(user_id))
        return render_template("user_details.html", user=user)
    

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return db.query(User).filter_by(id=user_id).first()

    if __name__ == '__main__':
        app.register_blueprint(main)
        app.run(debug=True)








