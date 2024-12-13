import requests
import random
from datetime import datetime, timedelta

# URL de l'API
url = "http://localhost:5000/factures"
types_conso = ["water", "electricity", "gas", "internet"]

# Fonction pour générer une date aléatoire à partir de la date d'aujourd'hui
def generate_random_date(start_date):
    days_offset = random.randint(0, 30)  # Génère une date dans le mois en cours
    return (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")

# Fonction pour envoyer une facture
def send_facture(consommation_type, logement_id, montant, consommee, date_fact):
    payload = {
        "type": consommation_type,
        "date_fact": date_fact,
        "montant": montant,
        "val_consommee": consommee,
        "logement_id": logement_id
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Envoi de la requête POST avec les données de la facture
    response = requests.post(url, json=payload, headers=headers)
    
    # Vérification de la réponse
    if response.status_code == 200:
        print(f"Facture {consommation_type} envoyée avec succès!")
    else:
        print(f"Erreur lors de l'envoi de la facture {consommation_type}: {response.status_code}")

# Fonction principale
def generate_factures():
    start_date = datetime.now()
    
    for consommation_type in types_conso:
        for i in range(10):  # Génère 10 factures pour chaque type de consommation
            date_fact = generate_random_date(start_date)
            montant = round(random.uniform(50.0, 150.0), 2)  # Montant aléatoire entre 50 et 150
            consommee = round(random.uniform(30.0, 200.0), 2)  # Consommation aléatoire entre 30 et 200
            logement_id = random.randint(1, 5)  # ID logement aléatoire entre 1 et 5

            # Envoie la facture
            send_facture(consommation_type, logement_id, montant, consommee, date_fact)

# Appel de la fonction pour générer les factures
generate_factures()
