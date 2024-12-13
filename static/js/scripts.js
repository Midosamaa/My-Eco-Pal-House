
//inscription
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("signupForm");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();  // Empêche l'envoi classique du formulaire

        // Vérification des mots de passe
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;
        if (password !== confirmPassword) {
            alert("Les mots de passe ne correspondent pas.");
            return; // Stoppe l'exécution du script
        }

        // Envoi des données via fetch
        const formData = new FormData(form);
        try {
            const response = await fetch('/inscription', {
                method: 'POST',
                body: formData
            });

            // Traitement de la réponse
            const data = await response.json();

            if (response.status === 400 && data.error) {
                // Afficher un message d'erreur spécifique si l'email existe déjà
                alert(data.error);
                return;
            }

            if (response.ok) {
                alert("Inscription réussie !");
                window.location.href = '/'; // Redirection vers la page de connexion
            } else {
                alert("Une erreur s'est produite. Veuillez réessayer.");
            }
        } catch (error) {
            console.error("Erreur:", error);
            alert("Erreur de communication avec le serveur.");
        }
    });
});
//login
document.addEventListener("DOMContentLoaded", function () {
    // Script pour la page de connexion
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault(); // Empêche le rechargement de la page

            const formData = new FormData(loginForm);

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.status === "error") {
                    alert(data.message); // Affiche un message d'erreur en cas d'échec
                    return;
                }

                // Connexion réussie, redirige vers la page home
                alert(data.message);
                window.location.href = "/home"; // Redirection correcte
            } catch (error) {
                console.error("Erreur:", error);
                alert("Erreur de communication avec le serveur.");
            }
        });
    }
});
//change pwrd
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("changePasswordForm");
    const confirmBtn = document.getElementById("confirmBtn");
    
    // Lorsque le bouton "Changer le mot de passe" est cliqué
    confirmBtn.addEventListener("click", function (event) {
        const newPassword = document.getElementById("newPassword")? document.getElementById("newPassword").value : null;
        const confirmPassword = document.getElementById("confirmPassword")? document.getElementById("confirmPassword").value : null;
        const currentPassword = document.getElementById("currentPassword") ? document.getElementById("currentPassword").value : null;

        // Vérification que tous les champs sont remplis
        if (!currentPassword || !newPassword || !confirmPassword) {
            event.preventDefault();  // Empêche la soumission du formulaire
            alert("Remplissez tous les champs.");
        } else if (newPassword !== confirmPassword) {
            event.preventDefault();  // Empêche la soumission du formulaire
            alert("Les nouveaux mots de passe ne correspondent pas.");
        } else {
            // Si les mots de passe sont valides, on affiche un message et on redirige
            alert("Mot de passe changé avec succès!");
            window.location.href = "/home";  // Redirige vers la page d'accueil
        }
    });
});


// Lorsque le bouton "Annuler" est cliqué
document.getElementById("cancelBtn").addEventListener("click", function () {
    window.location.href = "/home";  // Redirige vers la page d'accueil
});


//consommation

document.addEventListener("DOMContentLoaded", function () {
    // Vérifiez si la variable consommations existe
    if (typeof consommations === "undefined") {
        console.error("Les données de consommations ne sont pas disponibles.");
        return;
    }

    // Créez le graphique en camembert
    createPieChart(consommations);

    // Fonction pour afficher les détails de consommation
    function showConsumptionDetails(consommationType) {
        console.log("Type cliqué :", consommationType);

        // Vérifiez si les éléments HTML nécessaires existent
        var chartsContainer = document.getElementById("charts-container");
        var tableBody = document.getElementById("tableBody");
        var lineChartCanvas = document.getElementById("lineChart");

        if (!chartsContainer || !tableBody || !lineChartCanvas) {
            console.error("Impossible d'afficher les détails de consommation. Certains éléments manquent.");
            return;
        }

        // Affichez les éléments nécessaires
        chartsContainer.classList.remove("hidden");
        document.getElementById("consumptionTable").classList.remove("hidden");

        // Remplir le tableau
        tableBody.innerHTML = ""; // Réinitialise le tableau
        consommations[consommationType].forEach(function (entry) {
            var row = document.createElement("tr");
            row.innerHTML = `
                <td>${entry.date}</td>
                <td>${entry.consommation} kWh</td>
                <td>${entry.montant.toFixed(2)} €</td>
            `;
            tableBody.appendChild(row);
        });

        // Met à jour le graphique en ligne
        updateLineChart(consommationType);
    }

    // Créez le graphique en camembert
    function createPieChart(consommations) {
        var ctx = document.getElementById("consommationPieChart").getContext("2d");
        var data = {
            labels: ['Électricité', 'Eau', 'Gaz', 'Internet'],
            datasets: [{
                data: [
                    consommations.electricity.reduce((sum, item) => sum + item.consommation, 0),
                    consommations.water.reduce((sum, item) => sum + item.consommation, 0),
                    consommations.gas.reduce((sum, item) => sum + item.consommation, 0),
                    consommations.internet.reduce((sum, item) => sum + item.consommation, 0)
                ],
                backgroundColor: ['#4bc0c0', '#36a2eb', '#ff6384', '#ffcc00']
            }]
        };

        new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                return tooltipItem.label + ': ' + tooltipItem.raw.toFixed(2) + ' kWh';
                            }
                        }
                    }
                },
                onClick: function (event, activeElements) {
                    if (activeElements.length > 0) {
                        var index = activeElements[0].index;
                        var consommationTypeMap = ['electricity', 'water', 'gas', 'internet'];
                        var consommationType = consommationTypeMap[index];
                        showConsumptionDetails(consommationType);
                    }
                }
            }
        });
    }

    // Met à jour le graphique en ligne
    function updateLineChart(consommationType) {
        var ctx = document.getElementById("lineChart").getContext("2d");
        var labels = consommations[consommationType].map(entry => entry.date);
        var data = consommations[consommationType].map(entry => entry.consommation);

        if (window.lineChartInstance) {
            window.lineChartInstance.destroy();
        }

        window.lineChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Consommation ${consommationType} sur les 30 derniers jours`,
                    data: data,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)'
                }]
            },
            options: { responsive: true }
        });
    }
});
