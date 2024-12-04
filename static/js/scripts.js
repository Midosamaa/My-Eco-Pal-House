
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
