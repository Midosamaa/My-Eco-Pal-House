from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)

# Fonction pour créer une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect("../database/logement.db")  # Remplace par le chemin vers ta base
    conn.row_factory = sqlite3.Row
    return conn

# Route pour afficher la page d'inscription
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Vérification des mots de passe
        if password != confirm_password:
            return "Les mots de passe ne correspondent pas", 400

        # Hash du mot de passe pour plus de sécurité
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Insérer dans la base de données
        conn = get_db_connection()
        try:
            # Insérer dans la table logement
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logement (IP, adress, num_tel) VALUES (?, ?, ?)",
                (None, adresse, telephone)
            )
            logement_id = cursor.lastrowid  # Récupérer l'ID du logement inséré

            # Insérer dans la table users
            cursor.execute(
                "INSERT INTO users (name, logement_id, password_hash) VALUES (?, ?, ?)",
                (f"{prenom} {nom}", logement_id, password_hash)
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            return f"Une erreur est survenue : {e}", 500
        finally:
            conn.close()

        return redirect(url_for('success'))  # Rediriger après succès

    return render_template('inscription.html')

# Route de succès (page simple)
@app.route('/success')
def success():
    return "Inscription réussie !"

if __name__ == '__main__':
    app.run(debug=True)
