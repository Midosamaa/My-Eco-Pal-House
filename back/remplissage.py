from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime
import requests  # Importer la bibliothèque requests pour les appels API

app = Flask(__name__)

# Fonction de connexion à la base de données
def connect_db():
    conn = sqlite3.connect('logement.db')
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par leur nom
    return conn

# Route GET pour récupérer toutes les mesures
@app.route('/mesures', methods=['GET'])
def get_mesures():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mesure')
    mesures = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in mesures])

# Route POST pour ajouter une nouvelle mesure
@app.route('/mesures', methods=['POST'])
def add_mesure():
    data = request.json
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mesure (ID_capt_act, value, date_insertion)
        VALUES (?, ?, ?)
    ''', (data['ID_capt_act'], data['value'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
    # Récupérer la clé API d'OpenWeatherMap
    api_key = 'YOUR_API_KEY'  # Remplace avec ta clé API
    city = 'Paris'  # Remplace avec la ville de ton choix
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&cnt=40&units=metric&appid={api_key}'

    # Appel API pour obtenir les prévisions météo à 5 jours
    response = requests.get(url)
    data = response.json()

    # Vérification si la requête a réussi
    if response.status_code == 200:
        forecast = []
        for item in data['list']:
            # Récupérer la date et l'heure
            dt_utc = datetime.utcfromtimestamp(item['dt'])
            date = dt_utc.strftime('%Y-%m-%d')
            
            # Filtrer les prévisions par date, par exemple à 12h chaque jour
            if dt_utc.hour == 12:  # Prendre la prévision pour 12h chaque jour
                temperature = item['main']['temp']
                description = item['weather'][0]['description']
                forecast.append({'date': date, 'temperature': temperature, 'description': description})

        # Rendu de la page avec les prévisions météo
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
