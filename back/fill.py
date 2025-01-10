import requests
import random
from datetime import datetime, timedelta

# URL de l'API
url = "http://localhost:5000/factures"
types_conso = ["water", "electricity", "gas", "internet"]

# Mean consumption and price ranges for each type
consumption_data = {
    "water": {"mean": 54, "std_dev": 30, "price_per_unit": 4.34},
    "electricity": {"mean": 500, "std_dev": 50, "price_per_unit": 0.2516},
    "gas": {"mean": 300, "std_dev": 40, "price_per_unit": 1.025 },
    "internet": {"mean": 500, "std_dev": 100, "price_per_unit": 0.1},
}

# Function to generate a date in a specific month
def generate_date_for_month(month_offset):
    today = datetime.now()
    year = today.year
    month = today.month - month_offset
    if month <= 0:
        month += 12
        year -= 1
    day = random.randint(1, 28)  # Simplified to avoid edge cases with different month lengths
    return datetime(year, month, day).strftime("%Y-%m-%d")

# Function to send a bill
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
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Facture {consommation_type} envoyée avec succès!")
    else:
        print(f"Erreur lors de l'envoi de la facture {consommation_type}: {response.status_code}")

# Main function
def generate_factures():
    for consommation_type in types_conso:
        mean = consumption_data[consommation_type]["mean"]
        std_dev = consumption_data[consommation_type]["std_dev"]
        price_per_unit = consumption_data[consommation_type]["price_per_unit"]

        for i in range(5):  # Generate 5 invoices per type
            date_fact = generate_date_for_month(i)
            consommee = max(0, round(random.gauss(mean, std_dev), 2))  # Ensure no negative values
            montant = round(consommee * price_per_unit, 2)
            logement_id = 2  # Replace with logic for dynamic IDs if needed
            send_facture(consommation_type, logement_id, montant, consommee, date_fact)

# Call the function to generate invoices
generate_factures()
