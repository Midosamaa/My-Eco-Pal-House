from flask import Flask, request, jsonify, render_template_string, render_template, session, redirect, url_for,flash
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt  # Import de la bibliothèque MQTT
import json  # Pour traiter les messages JSON
import hashlib
from datetime import datetime
import requests
import random

app = Flask(__name__, template_folder="../front/html", static_folder="../static")
CORS(app)
app.secret_key = "cle tres secrete mec de ouf"

@app.route('/', methods=['GET'])
def home_page():
    return render_template('login.html')


@app.route('/inscription')
def inscription_page():
    return render_template('inscription.html')

@app.route('/test_session')
def test_session():
    # Stocker une valeur dans la session
    session['test_key'] = 'Session activée !'
    return "Valeur ajoutée dans la session."

@app.route('/check_session')
def check_session():
    valeur = session.get('test_key', 'Aucune valeur trouvée dans la session.')
    return f"Valeur dans la session : {valeur}"


#################################################
# Fonction de connexion à la base de données
def connect_db():
    conn = sqlite3.connect('../database/logement.db')
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par leur nom
    return conn

#################################################

@app.route('/consommation', methods=['GET', 'POST'])
def consommation():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))

    # Paramètre de filtrage (par mois, année ou tout)
    selected_period = request.args.get('period', 'month')

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT logement_id FROM users WHERE id = ?", (user_id,))
    logement_row = cursor.fetchone()

    if logement_row is None:
        return "Logement introuvable", 404

    logement_id = logement_row[0]

    # Calcul de la date pour le filtrage
    if selected_period == 'month':
        date_filter = datetime.now().strftime('%Y-%m')
        cursor.execute("""
            SELECT type, date_fact, val_consommee, montant
            FROM facture
            WHERE logement_id = ?
            ORDER BY type, date_fact
        """, (logement_id,))

    elif selected_period == 'year':
        year_filter = datetime.now().strftime('%Y')
        cursor.execute("""
            SELECT type, date_fact, val_consommee, montant
            FROM facture
            WHERE logement_id = ? AND date_fact LIKE ?
            ORDER BY date_fact
        """, (logement_id, f'{year_filter}%'))
    else:
        cursor.execute("""
            SELECT type, date_fact, val_consommee, montant
            FROM facture
            WHERE logement_id = ?
            ORDER BY date_fact
        """, (logement_id,))

    factures = cursor.fetchall()

    consommations = {
        'electricity': [],
        'water': [],
        'gas': [],
        'internet': []  # Ajout de l'internet
    }

    for type_conso, date, consommee, montant in factures:
        if type_conso in consommations:
            consommations[type_conso].append({
                'date': date,
                'consommation': consommee,
                'montant': montant
            })
        else:
            print(f"Type inconnu ignoré : {type_conso}")

    conn.close()

    return render_template('consommation.html', consommations=consommations, period=selected_period)


@app.route('/api/latest-consumption', methods=['GET'])
def latest_consumption():
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT logement_id FROM users WHERE id = ?", (user_id,))
    logement_row = cursor.fetchone()

    if logement_row is None:
        return jsonify({'error': 'Logement introuvable'}), 404

    logement_id = logement_row[0]
    date_filter = datetime.now().strftime('%Y-%m-%d')

    # Fetch the latest consumption for each type
    cursor.execute("""
        SELECT type, val_consommee, date_fact
        FROM facture
        WHERE logement_id = ? AND date_fact LIKE ?
        GROUP BY type
        ORDER BY date_fact DESC
    """, (logement_id, f'{date_filter}%'))

    latest_consumptions = cursor.fetchall()

    # Format the results
    consumption_data = {}
    for type_conso, val_consommee, date_fact in latest_consumptions:
        consumption_data[type_conso] = {
            'date': date_fact,
            'consumption': val_consommee
        }

    conn.close()
    return jsonify(consumption_data)

@app.route('/factures/<int:id>', methods=['DELETE'])
def supprimer_facture(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Supprimer la facture avec l'id donné
        cursor.execute("DELETE FROM facture WHERE id = ?", (id,))
        conn.commit()

        # Vérifiez si une facture a été supprimée
        if cursor.rowcount == 0:
            return jsonify({"error": "Facture non trouvée"}), 404

        return jsonify({"message": "Facture supprimée avec succès"}), 200

    except Exception as e:
        print("Erreur lors de la suppression de la facture :", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/capteurs', methods=['GET', 'POST'])
def capteurs():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))  # Redirect if not logged in

    conn = connect_db()  # Assuming connect_db() connects to your SQLite database
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle state update for sensors or actuators
        sensor_id = request.form.get('sensor_id')
        new_state = request.form.get('new_state')

        if sensor_id and new_state:
            # Update the state of the sensor/actionneur in the database
            cursor.execute("""
                UPDATE capt_act
                SET etat = ?
                WHERE ID = ?
            """, (new_state, sensor_id))
            conn.commit()

    # Fetch the logement_id associated with the logged-in user
    cursor.execute("SELECT logement_id FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result is None:
        return "No logement found for this user", 404  # Handle case where no logement is found for the user

    logement_id = result[0]  # Extract logement_id from the tuple

    # Query the house with the logement_id
    cursor.execute("SELECT * FROM logement WHERE id = ?", (logement_id,))
    house = cursor.fetchone()

    # Query rooms in the house based on the logement_id
    cursor.execute("SELECT * FROM piece WHERE logement_id = ?", (logement_id,))
    rooms = cursor.fetchall()

    # Query sensors/actuators in the rooms
    cursor.execute("""
        SELECT capt_act.*, piece.name AS room_name
        FROM capt_act
        JOIN piece ON capt_act.ref_piece = piece.ID
        WHERE piece.logement_id = ?
    """, (logement_id,))
    sensors_and_actuators = cursor.fetchall()

    # Close the connection
    conn.close()

    # Render the template with data
    return render_template('capteurs.html', house=house, rooms=rooms, sensors_and_actuators=sensors_and_actuators)

@app.route('/economies')
def economies():
    return render_template('economies.html')

@app.route('/configuration')
def configuration():
    return render_template('configuration.html')

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    # Vérifie si l'utilisateur est connecté (session)
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirige vers la page de connexion si non authentifié

    if request.method == 'POST':
        # Récupère les champs du formulaire
        current_password = request.form.get('currentPassword')
        new_password = request.form.get('newPassword')
        confirm_password = request.form.get('confirmPassword')

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Récupère le mot de passe hashé de l'utilisateur actuel
            cursor.execute('SELECT password_hash FROM users WHERE id = ?', (session['user_id'],))
            user = cursor.fetchone()

            if not user:
                return jsonify({"status": "error", "message": "Utilisateur non trouvé."}), 400

            stored_password_hash = user[0]

            # Vérifie que le mot de passe actuel correspond à celui stocké dans la base de données
            if hashlib.sha256(current_password.encode()).hexdigest() != stored_password_hash:
                return jsonify({"status": "error", "message": "Le mot de passe actuel est incorrect."}), 400

            # Vérifie que les nouveaux mots de passe correspondent
            if new_password != confirm_password:
                return jsonify({"status": "error", "message": "Les nouveaux mots de passe ne correspondent pas."}), 400

            # Hache le nouveau mot de passe
            new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()

            # Met à jour le mot de passe dans la base de données
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, session['user_id']))
            conn.commit()

            return jsonify({"status": "success", "message": "Mot de passe changé avec succès."}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": "Erreur interne."}), 500

    return render_template('change-password.html')  # Affiche le formulaire de changement de mot de passe
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')  # Rediriger vers la page de login après déconnexion





# Configuration MQTT
MQTT_BROKER = "192.168.53.254" #"172.20.10.2"  #"192.168.125.254" #"192.168.11.114" # "192.168.125.254" #"192.168.137.254" #"192.168.1.16"#192.168.172.254"#"192.168.1.17" #"192.168.231.254" #"192.168.1.17" #"172.20.10.3"#"192.168.28.254" #"192.168.6.254"  # Adresse de ton broker MQTT
MQTT_PORT = 1883  # Port par défaut de MQTT
MQTT_TOPIC = "maison/capteurs/dht11"  # Topic pour recevoir les données de température et d'humidité
LED_TOPIC = "maison/led"  # Topic pour envoyer des commandes pour allumer ou éteindre la LED

# Fonction appelée lors de la connexion au broker
def on_connect(client, userdata, flags, rc):
    print(f"Connecté au broker MQTT avec le code : {rc}")
    # S'abonner au topic des mesures de température
    client.subscribe(MQTT_TOPIC)

# Fonction appelée lorsqu'un message est reçu sur le topic
def on_message(client, userdata, msg):
    print(f"Message reçu sur le topic {msg.topic}: {msg.payload.decode()}")
    
    # Traiter les données JSON reçues
    try:
        data = json.loads(msg.payload.decode())
        temp = data.get('temperature')
        humid = data.get('humidity')
        
        if temp is not None and humid is not None:
            # Ajouter les données à la base de données
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO mesure (ID_capt_act, value, date_insertion)
                VALUES (?, ?, ?)
            ''', ('dht11', f"Temp: {temp}°C, Humid: {humid}%", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
            print(f"Mesure ajoutée: Temp: {temp}°C, Humid: {humid}%")

            # Si la température dépasse 29°C, allumer la LED
            if temp > 20:
                client.publish(LED_TOPIC, "ON")  # Allumer la LED
                print("LED allumée")
            else:
                client.publish(LED_TOPIC, "OFF")  # Éteindre la LED
                print("LED éteinte")

    except Exception as e:
        print(f"Erreur dans le traitement des données : {e}")
@app.route('/update_state', methods=['POST'])
def update_state():
    data = request.get_json()
    sensor_id = data.get('sensor_id')
    state = data.get('state')

    # Connect to the database
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Update the sensor state in the database
    cursor.execute("UPDATE capt_act SET etat = ? WHERE ID = ?", (state, sensor_id))
    conn.commit()

    # Close the database connection
    conn.close()

    return jsonify({'success': True})
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Vérifiez si l'utilisateur existe dans la base de données
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"status": "error", "message": "Adresse email non trouvée."}), 400

        user_id, password_hash = user

        # Vérifiez que le mot de passe correspond
        if hashlib.sha256(password.encode()).hexdigest() != password_hash:
            return jsonify({"status": "error", "message": "Mot de passe incorrect."}), 400

        # Connexion réussie, créez une session
        session['user_id'] = user_id
        return jsonify({"status": "success", "message": "Connexion réussie."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "Erreur interne."}), 500
    
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login_page')  # Redirige vers la page de connexion si non connecté
    return render_template('home.html')  # Charge la page uniquement si authentifié

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     return redirect('/login_page')  # Redirige vers la page de connexion après déconnexion


# Configuration du client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connexion au broker MQTT
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Démarrer un thread pour gérer la boucle MQTT
mqtt_client.loop_start()

@app.route('/inscription', methods=['POST'])
def inscription():
    prenom = request.form.get('prenom')
    nom = request.form.get('nom')
    adresse = request.form.get('adresse')
    telephone = request.form.get('telephone')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Vérifier que les mots de passe correspondent
    if password != confirm_password:
        return jsonify({"error": "Les mots de passe ne correspondent pas"}), 400

    # Hacher le mot de passe
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Vérifier si l'email existe déjà
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error": "Un compte avec cet e-mail existe déjà"}), 400

        # Insérer un nouveau logement
        cursor.execute('''
            INSERT INTO logement (IP, adress, num_tel)
            VALUES (?, ?, ?)
        ''', ('192.168.1.1', adresse, telephone))
        logement_id = cursor.lastrowid

        # Insérer l'utilisateur dans la table "users"
        cursor.execute('''
            INSERT INTO users (name, logement_id, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (f"{prenom} {nom}", logement_id, email, password_hash))

        conn.commit()
        conn.close()

        # Succès - pas besoin de render_template ici, JSON est mieux pour les requêtes AJAX
        return jsonify({"message": "Inscription réussie !"}), 200

    except sqlite3.IntegrityError as e:
        if "users.email" in str(e):
            return jsonify({"error": "Cet email existe déjà."}), 400
        return jsonify({"error": "Erreur lors de l'inscription."}), 500

    except Exception as e:
        return jsonify({"error": "Erreur interne."}), 500

# Route GET pour récupérer toutes les mesures
@app.route('/mesures', methods=['GET'])
def get_mesures():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mesure')
    mesures = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in mesures])

# Route POST pour ajouter une nouvelle mesure (température et humidité)
@app.route('/mesures', methods=['POST'])
def add_mesure():
    data = request.json
    
    # Vérification que les données sont présentes et valides
    temp = data.get('value', {}).get('temperature')
    humid = data.get('value', {}).get('humidity')
    
    if temp is None or humid is None:
        return jsonify({"error": "Données manquantes"}), 400
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Insérer les mesures de température et d'humidité dans la table "mesure"
    cursor.execute('''
        INSERT INTO mesure (ID_capt_act, value, date_insertion)
        VALUES (?, ?, ?)
    ''', (data['ID_capt_act'], f"Temp: {temp}°C, Humid: {humid}%", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

    return jsonify({"message": "Mesure ajoutée avec succès"}), 201

# Route POST pour créer une nouvelle facture
@app.route('/factures', methods=['POST'])
def create_facture():
    try:
        # Get data from the incoming request
        data = request.get_json()  # Assuming you're sending JSON data

        # Extract values from the JSON payload
        consommation_type = data['type']
        date_fact = data['date_fact']
        montant = data['montant']
        consommee = data['val_consommee']
        logement_id = data['logement_id']
        # Insert the data into the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO facture (type, date_fact, montant, val_consommee, logement_id)
            VALUES (?, ?, ?, ?, ?)
        """, (consommation_type, date_fact, montant, consommee, logement_id))
        conn.commit()
        conn.close()

        return jsonify({"message": "Facture created successfully!"}), 201  # Success response

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while creating the facture"}), 500

#Route pour la consommation
@app.route('/api/consommation', methods=['GET'])
def api_consommation():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT type, SUM(val_consommee) as total_consommee
        FROM facture
        GROUP BY type
    ''')
    data = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

@app.route('/api/economies', methods=['GET'])
def api_economies():
    conn = connect_db()
    cursor = conn.cursor()

    # Optionnel : Récupérer un type de facture via les paramètres de l'URL
    type_facture = request.args.get('type', None)  # Exemple : "electricity", "water", "gas"
    filtre_type = "WHERE type = ?" if type_facture else ""

    # Calcul des économies mensuelles
    query = f'''
        SELECT strftime('%Y-%m', date_fact) as mois, type, 
               SUM(val_consommee) as consommation_actuelle,
               AVG(SUM(val_consommee)) OVER (PARTITION BY type) as consommation_moyenne
        FROM facture
        {filtre_type}
        GROUP BY type, strftime('%Y-%m', date_fact)
        ORDER BY mois;
    '''

    cursor.execute(query, (type_facture,) if type_facture else ())
    
    data = []
    economies_totales = 0  # Variable pour accumuler les économies totales

    # Parcourir les résultats et calculer les économies mensuelles
    for row in cursor.fetchall():
        mois = row['mois']
        type_facture = row['type']
        consommation_actuelle = row['consommation_actuelle']
        consommation_moyenne = row['consommation_moyenne']
        economie = consommation_moyenne - consommation_actuelle if consommation_moyenne else 0

        # Ajouter les économies du mois à la somme totale
        economies_totales += max(economie, 0)  # Empêcher les économies négatives

        # Ajouter les données de chaque mois dans la réponse
        data.append({
            "mois": mois,
            "type": type_facture,
            "consommation_actuelle": consommation_actuelle,
            "consommation_moyenne": consommation_moyenne,
            "economie": economie
        })

    conn.close()

    # Retourner les économies mensuelles et les économies totales
    return jsonify({"economies_mensuelles": data, "economies_totales": round(economies_totales, 2)})


# Route GET pour afficher une page HTML avec un camembert des factures combinées par type
@app.route('/factures_chart', defaults={'logement_id': None}, methods=['GET'])
@app.route('/factures_chart/<int:logement_id>', methods=['GET'])
def afficher_factures_chart(logement_id):
    conn = connect_db()
    cursor = conn.cursor()

    if logement_id is None:
        cursor.execute('''
            SELECT type, SUM(montant) AS total_montant
            FROM facture
            GROUP BY type
        ''')
        title = "Répartition des Montants des Factures (Tous les Logements)"
    else:
        cursor.execute('''
            SELECT type, SUM(montant) AS total_montant
            FROM facture
            WHERE logement_id = ?
            GROUP BY type
        ''', (logement_id,))
        title = f"Répartition des Montants des Factures (Logement {logement_id})"

    factures = cursor.fetchall()
    conn.close()

    data_chart = [["Type de Facture", "Montant"]]
    for facture in factures:
        data_chart.append([facture['type'], facture['total_montant']])

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graphique des Factures</title>
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript">
            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(drawChart);

            function drawChart() {
                var data = google.visualization.arrayToDataTable({{ data|safe }});
                var options = {
                    title: '{{ title }}',
                    is3D: true
                };
                var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                chart.draw(data, options);
            }
        </script>
    </head>
    <body>
        <h2>{{ title }}</h2>
        <div id="piechart" style="width: 900px; height: 500px;"></div>
    </body>
    </html>
    """

    return render_template_string(template, data=data_chart, title=title)

# Route GET pour afficher les prévisions météo à 5 jours
@app.route('/weather', methods=['GET'])
def get_weather():
    api_key = 'e433b8f05f0e13c21887d09c227b23bd'  # Remplace avec ta clé API
    city = 'paris'  # Remplace avec la ville de ton choix
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&cnt=40&units=metric&appid={api_key}'

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        forecast = []
        for item in data['list']:
            dt_utc = datetime.utcfromtimestamp(item['dt'])
            date = dt_utc.strftime('%Y-%m-%d')
            
            if dt_utc.hour == 12:  # Prendre la prévision pour 12h chaque jour
                temperature = item['main']['temp']
                description = item['weather'][0]['description']
                forecast.append({'date': date, 'temperature': temperature, 'description': description})

        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prévisions Météo</title>
        </head>
        <body>
            <h2>Prévisions Météo pour les 5 prochains jours</h2>
            <table border="1">
                <tr>
                    <th>Date</th>
                    <th>Température (°C)</th>
                    <th>Description</th>
                </tr>
                {% for day in forecast %}
                <tr>
                    <td>{{ day.date }}</td>
                    <td>{{ day.temperature }}°C</td>
                    <td>{{ day.description }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(template, forecast=forecast)
    
    else:
        return jsonify({"error": "Impossible de récupérer les prévisions météo"}), 400

@app.route('/add_facture', methods=['POST'])
def add_facture():
    # Récupérer les données du formulaire
    type_facture = request.form['type']
    date_facture = request.form['date_fact']
    montant = float(request.form['montant'])
    val_consommee = float(request.form['val_consommee'])

    # Connexion à la base de données
    # Get the user ID from the session
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))  # Redirect if not logged in

    conn = connect_db()  # Assuming connect_db() connects to your SQLite database
    cursor = conn.cursor()

    # Fetch the logement_id associated with the logged-in user
    cursor.execute("SELECT logement_id FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result is None:
        return "No logement found for this user", 404  # Handle case where no logement is found for the user

    logement_id = result[0]  # Extract logement_id from the tuple
    # Insertion dans la base de données
    cursor.execute("""
        INSERT INTO facture (type, date_fact, montant, val_consommee, logement_id)
        VALUES (?, ?, ?, ?, ?)
    """, (type_facture, date_facture, montant, val_consommee, logement_id))

    # Sauvegarder les changements et fermer la connexion
    conn.commit()
    conn.close()

    return redirect(url_for('configuration'))  # Redirige vers la page de configuration

@app.route('/add_capt_act', methods=['POST'])
def add_capt_act():
    # Extract data from the form submission
    ref_commande = request.form['ref_commande']
    type_ = request.form['type']
    mesure = request.form.get('mesure', None)  # Optional field
    port_com = request.form['port_com']
    ref_piece = int(request.form['ref_piece'])  # Room ID
    etat = request.form.get('etat', 'off')  # Default state is 'off'

    # Retrieve user ID from the session
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Connect to the database
    conn = connect_db()  # Replace with your actual DB connection function
    cursor = conn.cursor()

    try:
        # Verify that the specified room belongs to the logged-in user
        cursor.execute('''
            SELECT p.id
            FROM piece p
            JOIN users u ON p.logement_id = u.logement_id
            WHERE p.id = ? AND u.id = ?
        ''', (ref_piece, user_id))
        piece_exists = cursor.fetchone()

        if not piece_exists:
            return "Room not found or not associated with the current user", 404

        # Insert the new capt/act into the database
        cursor.execute('''
            INSERT INTO capt_act (ref_commande, type, mesure, port_com, ref_piece, etat)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ref_commande, type_, mesure, port_com, ref_piece, etat))

        # Commit the transaction
        conn.commit()
        return redirect(url_for('configuration'))  # Redirect to the configuration page

    except Exception as e:
        # Rollback in case of an error
        conn.rollback()
        print(f"Error while adding capt/act: {e}")
        return "An error occurred while adding the capt/act.", 500

    finally:
        # Close the database connection
        conn.close()

@app.route('/get_rooms_and_capt_act', methods=['GET'])
def get_rooms_and_capt_act():
    try:
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({"error": "User not logged in"}), 401

        conn = connect_db()
        cursor = conn.cursor()

        # Get logement_id for the user
        cursor.execute("SELECT logement_id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result is None:
            return jsonify({"error": "No logement found"}), 404

        logement_id = result[0]
        # Fetch rooms and their capt/act
        cursor.execute("""
            SELECT p.name AS room_name, p.ID AS room_id, 
                   c.type AS capt_act_type, c.ref_commande AS capt_act_ref, c.etat AS capt_act_state
            FROM piece p
            LEFT JOIN capt_act c ON p.ID = c.ref_piece
            WHERE p.logement_id = ?
        """, (logement_id,))
        data = cursor.fetchall()

        conn.close()

        # Transform the data for JSON
        rooms_with_capt_act = []
        for row in data:
            rooms_with_capt_act.append({
                "room_name": row[0],
                "room_id": row[1],
                "capt_act_type": row[2],
                "capt_act_ref": row[3],
                "capt_act_state": row[4]
            })

        return jsonify(rooms_with_capt_act)

    except Exception as e:
        print(f"Error in /get_rooms_and_capt_act: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
