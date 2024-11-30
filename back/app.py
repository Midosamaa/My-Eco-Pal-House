import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Configuration de l'application Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle d'utilisateur
class User(db.Model):
    __tablename__ = 'users'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logement_id = db.Column(db.Integer, db.ForeignKey('logement.ID'), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    logement = db.relationship('Logement', backref='users', uselist=False)

# Modèle de logement
class Logement(db.Model):
    __tablename__ = 'logement'
    ID = db.Column(db.Integer, primary_key=True)
    IP = db.Column(db.String(50))
    adress = db.Column(db.String(255))
    num_tel = db.Column(db.String(15))
    date_insertion = db.Column(db.DateTime, default=db.func.current_timestamp())

# Créer la base de données (si elle n'existe pas encore)
with app.app_context():
    db.create_all()

# Page d'inscription
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']
        ip_address = request.form['ip_address']

        # Vérifier si le mot de passe et la confirmation sont identiques
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return redirect(url_for('inscription'))

        # Vérifier si l'email existe déjà
        existing_user = User.query.filter_by(name=email).first()
        if existing_user:
            flash('Un utilisateur avec cet email existe déjà.', 'error')
            return redirect(url_for('inscription'))

        # Hacher le mot de passe
        hashed_password = generate_password_hash(password)

        # Créer un nouveau logement
        new_logement = Logement(IP=ip_address, adress=address, num_tel=phone_number)

        # Ajouter le nouveau logement à la base de données
        db.session.add(new_logement)
        db.session.commit()  # Commit pour récupérer l'ID du logement

        # Créer un nouvel utilisateur avec le logement associé
        new_user = User(name=f"{first_name} {last_name}", password_hash=hashed_password, logement_id=new_logement.ID)

        # Ajouter l'utilisateur à la base de données
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))

    return render_template('inscription.html')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(name=email).first()

        if user and check_password_hash(user.password_hash, password):
            flash('Connexion réussie !', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')

    return render_template('login.html')

# Page d'accueil
@app.route('/accueil')
def accueil():
    return render_template('accueil.html')

if __name__ == '__main__':
    app.run(debug=True)
