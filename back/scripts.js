document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour récupérer les données de consommation
    function getConsommation() {
        fetch('http://localhost:5000/api/consommation')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur réseau : ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                let electricitySummary = 0;
                let waterSummary = 0;

                // Boucle à travers les données pour assigner les valeurs
                data.forEach(item => {
                    if (item.type === 'électricité') {
                        electricitySummary = item.total_consommee;
                    } else if (item.type === 'eau') {
                        waterSummary = item.total_consommee;
                    }
                });

                // Mise à jour des éléments HTML avec les valeurs récupérées
                document.getElementById('electricity-summary').textContent = electricitySummary + " kWh";
                document.getElementById('water-summary').textContent = waterSummary + " L";
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des données de consommation:', error);
                // Affichage d'un message d'erreur en cas de problème
                document.getElementById('electricity-summary').textContent = 'Erreur';
                document.getElementById('water-summary').textContent = 'Erreur';
            });
    }

    // Fonction pour récupérer les économies réalisées
    function getEconomies() {
        fetch('http://localhost:5000/api/economies')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur réseau : ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                let savingsSummary = 0;

                // Boucle à travers les données pour cumuler les économies réalisées
                data.forEach(item => {
                    savingsSummary += item.economie;
                });

                // Mise à jour de l'élément HTML avec les économies réalisées
                document.getElementById('savings-summary').textContent = savingsSummary.toFixed(2) + " €";
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des économies:', error);
                // Affichage d'un message d'erreur en cas de problème
                document.getElementById('savings-summary').textContent = 'Erreur';
            });
    }

    // Fonction pour générer le graphique de consommation
    function generateConsumptionChart() {
        fetch('http://localhost:5000/api/consommation')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur réseau : ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                const labels = [];
                const consumptionData = [];
                
                // Boucle pour extraire les données nécessaires pour le graphique
                data.forEach(item => {
                    labels.push(item.type);
                    consumptionData.push(item.total_consommee);
                });

                // Création du graphique avec Chart.js
                const ctx = document.getElementById('consumptionChart').getContext('2d');
                const consumptionChart = new Chart(ctx, {
                    type: 'bar',  // Type de graphique (barres)
                    data: {
                        labels: labels,  // Labels des types de consommation (électricité, eau, etc.)
                        datasets: [{
                            label: 'Consommation (kWh)',  // Légende du graphique
                            data: consumptionData,  // Données des consommations
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',  // Couleur de fond des barres
                            borderColor: 'rgba(75, 192, 192, 1)',  // Couleur du bord des barres
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true  // Commence à zéro sur l'axe Y
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des données du graphique:', error);
                // Affichage d'un message d'erreur en cas de problème
                document.getElementById('consumptionChart').textContent = 'Erreur lors de la récupération des données';
            });
    }

    // Appels des fonctions pour récupérer les données et générer le graphique au chargement de la page
    getConsommation();
    getEconomies();
    generateConsumptionChart();
});
