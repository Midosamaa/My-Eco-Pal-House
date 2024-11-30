from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt  # Import de la bibliothèque MQTT
import json  # Pour traiter les messages JSON

app = Flask(__name__)
CORS(app)

# Fonction de connexion à la base de données
def connect_db():
    conn = sqlite3.connect('logement.db')
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par leur nom
    return conn

# Configuration MQTT
MQTT_BROKER = "192.168.1.17" #"192.168.6.254"  # Adresse de ton broker MQTT
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
            if temp > 25:
                client.publish(LED_TOPIC, "ON")  # Allumer la LED
                print("LED allumée")
            else:
                client.publish(LED_TOPIC, "OFF")  # Éteindre la LED
                print("LED éteinte")

    except Exception as e:
        print(f"Erreur dans le traitement des données : {e}")

# Configuration du client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connexion au broker MQTT
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Démarrer un thread pour gérer la boucle MQTT
mqtt_client.loop_start()

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

# Route GET pour récupérer toutes les factures
@app.route('/factures', methods=['GET'])
def get_factures():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM facture')
    factures = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in factures])

#Route pour la consommation
@app.route('/api/consommation', methods=['GET'])
def consommation():
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

# Route POST pour ajouter une nouvelle facture
@app.route('/factures', methods=['POST'])
def add_facture():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO facture (type, date_fact, montant, val_consommee, logement_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['type'], data['date_fact'], data['montant'], data['val_consommee'], data['logement_id']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Facture ajoutée avec succès"}), 201

#Route pour les économies
@app.route('/api/economies', methods=['GET'])
def economies():
    conn = connect_db()
    cursor = conn.cursor()
    # Calcul d'exemple : différence entre consommation actuelle et une moyenne historique
    cursor.execute('''
        SELECT type, SUM(val_consommee) as consommation_actuelle,
        AVG(val_consommee) as consommation_moyenne
        FROM facture
        GROUP BY type
    ''')
    data = []
    for row in cursor.fetchall():
        type_facture = row['type']
        consommation_actuelle = row['consommation_actuelle']
        consommation_moyenne = row['consommation_moyenne']
        economie = consommation_moyenne - consommation_actuelle if consommation_moyenne else 0
        data.append({"type": type_facture, "economie": economie})
    conn.close()
    return jsonify(data)


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

if __name__ == '__main__':
    app.run(debug=True)
