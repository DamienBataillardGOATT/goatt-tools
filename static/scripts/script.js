        var panier = [];

        var creneauxDisponibles = {}; // Pour stocker les créneaux disponibles

        function updatePrix() {
            var selectElement = document.getElementById('cordage_id');
            var prixUnitaire = selectElement.options[selectElement.selectedIndex].getAttribute('data-prix');
            var quantite = document.getElementById('cordage_quantite').value;
            var prixTotal = prixUnitaire * quantite;
            document.getElementById('prix_cordage').textContent = 'Prix: ' + prixTotal.toFixed(2) + ' €';
        }

        // Ajouter un écouteur d'événements sur le champ de quantité
        document.getElementById('cordage_quantite').addEventListener('change', updatePrix);

        // Mettre à jour le prix initial lors du chargement de la page
        document.addEventListener('DOMContentLoaded', function() {
            updatePrix();
        });
        
        function ajouterAuPanier() {
            var selectElement = document.getElementById('cordage_id');
            var marque = selectElement.value;
            var prix = selectElement.options[selectElement.selectedIndex].getAttribute('data-prix');
            var quantite = document.getElementById('cordage_quantite').value;
            var totalArticle = prix * quantite;

            panier.push({ marque: marque, quantite: quantite, prix: prix, totalArticle: totalArticle });
            afficherPanier();
        }

        function afficherPanier() {
            var listePanier = document.getElementById('listePanier');
            var totalPanier = document.getElementById('totalPanier');
            var inputPrixTotalPanier = document.getElementById('prixTotalPanier');
            var total = 0;

            listePanier.innerHTML = '';

            panier.forEach(function(article, index) {
                var li = document.createElement('li');
                li.textContent = article.marque + ' x ' + article.quantite + ' : ' + article.totalArticle + ' €';
                
                // Créer un bouton de suppression
                var btnSupprimer = document.createElement('button');
                btnSupprimer.textContent = 'Supprimer';
                btnSupprimer.onclick = function() { supprimerDuPanier(index); }; // Fonction de suppression
                li.appendChild(btnSupprimer);

                listePanier.appendChild(li);

                total += parseFloat(article.totalArticle);
            });

            totalPanier.textContent = total.toFixed(2);
            inputPrixTotalPanier.value = total.toFixed(2);
        }

        function supprimerDuPanier(index) {
            panier.splice(index, 1); // Supprime l'article du tableau
            afficherPanier(); // Met à jour l'affichage du panier
        }

        // Fonction pour récupérer les créneaux disponibles et les afficher dans le menu déroulant
        function recupererEtAfficherCreneaux() {
            fetch('https://goatt-db.onrender.com/get_available_slots')
                .then(response => response.json())
                .then(data => {
                    creneauxDisponibles = data; // Stocker les données
                    const selectElement = document.getElementById('date_recuperation');
                    selectElement.innerHTML = ''; // Effacer les options existantes

                    // Boucler sur les données pour ajouter les options de date
                    for (const date in data) {
                        const option = document.createElement('option');
                        option.value = date;
                        option.textContent = date;
                        selectElement.appendChild(option);
                    }

                    // Afficher les créneaux pour la première date disponible
                    afficherCreneauxPourDate();
                })
                .catch(error => {
                    console.error('Erreur lors de la récupération des créneaux disponibles', error);
                });
        }

        // Fonction pour décomposer les créneaux en heures individuelles et créer des boutons pour chaque heure
        function afficherHeuresPourCreneau(creneau, date) {
            const heures = creneau.split('-'); // Exemple: "10h - 12h" devient ["10h ", " 12h"]
            const heureDebut = parseInt(heures[0]); // Exemple: "10h " devient 10
            const heureFin = parseInt(heures[1]); // Exemple: " 12h" devient 12
            const container = document.getElementById('creneauxHorairesContainer');

            // Créer un bouton pour chaque heure dans l'intervalle, y compris l'heure de fin
            for (let heure = heureDebut; heure <= heureFin; heure++) {
                const bouton = document.createElement('button');
                bouton.type = 'button'; // Assurez-vous de définir le type sur 'button'
                bouton.textContent = `${heure}h`; // Exemple: "10h"
                bouton.value = `${date} ${heure}h`;
                bouton.classList.add('creneau-btn'); // Ajouter une classe pour le style
                bouton.onclick = function(event) {
                    event.preventDefault(); // Empêche la soumission du formulaire
                    choisirCreneau(this.value);
                };
                container.appendChild(bouton);
            }
        }

        // Fonction pour afficher les boutons de créneaux horaires pour la date sélectionnée
        function afficherCreneauxPourDate(dateSelectionnee, creneauxPourDate) {
            const container = document.getElementById('creneauxHorairesContainer');
            container.innerHTML = '';

            // Créer un bouton pour chaque créneau horaire et le décomposer en heures
            creneauxPourDate.forEach(creneau => {
                afficherHeuresPourCreneau(creneau.trim(), dateSelectionnee);
            });
        }

        function extraireHeure(creneau) {
        // Utilisez une expression régulière pour trouver les chiffres avant le 'h'
        const resultat = creneau.match(/(\d+)h/);

        // Vérifiez si le résultat n'est pas nul et renvoyez le premier groupe capturé
        if (resultat && resultat[1]) {
            return parseInt(resultat[1], 10); // Convertissez le résultat en nombre
        } else {
            console.error('Format de créneau invalide');
            return null; // ou vous pouvez renvoyer une valeur par défaut ou lever une erreur
        }
        }

        // Fonction pour gérer la sélection d'un créneau horaire
        function choisirCreneau(heure) {
            console.log('Heure sélectionnée:', heure);
            const heuresansdate = extraireHeure(heure);
            // Mettre à jour le champ caché avec la valeur de l'heure sélectionnée
            document.getElementById('creneauSelectionne').value = heuresansdate;
        }

        document.getElementById('magasin_recuperation').addEventListener('change', function() {
            var adresseMagasin = this.options[this.selectedIndex].getAttribute('data-adresse');
            document.getElementById('adresse_magasin').value = adresseMagasin;
        });

        document.getElementById('magasin_livraison').addEventListener('change', function() {
            var adresseMagasin = this.options[this.selectedIndex].getAttribute('data-adresse');
            document.getElementById('adresse_magasin').value = adresseMagasin;
        });

        // Script pour afficher/cacher les champs en fonction de l'option de récupération choisie
        document.addEventListener('DOMContentLoaded', function() {
            var recuperationOptions = document.querySelectorAll('input[name="option_recuperation"]');
            recuperationOptions.forEach(function(option) {
                option.addEventListener('change', function() {
                    if (this.value === 'adresse') {
                        document.getElementById('adresse_recuperation_container').style.display = 'block';
                        document.getElementById('magasin_recuperation_container').style.display = 'none';
                    } else if (this.value === 'magasin') {
                        document.getElementById('adresse_recuperation_container').style.display = 'none';
                        document.getElementById('magasin_recuperation_container').style.display = 'block';
                    }
                });
            });

            var livraisonOptions = document.querySelectorAll('input[name="option_livraison"]');
            livraisonOptions.forEach(function(option) {
                option.addEventListener('change', function() {
                    if (this.value === 'adresse') {
                        document.getElementById('adresse_livraison_container').style.display = 'block';
                        document.getElementById('magasin_livraison_container').style.display = 'none';
                    } else if (this.value === 'magasin') {
                        document.getElementById('adresse_livraison_container').style.display = 'none';
                        document.getElementById('magasin_livraison_container').style.display = 'block';
                    }
                });
            });
            
            // Récupérer et afficher les créneaux disponibles
            recupererEtAfficherCreneaux();
            document.getElementById('date_recuperation').addEventListener('change', function() {
                const dateSelectionnee = this.value;
                const creneauxPourDate = creneauxDisponibles[dateSelectionnee] || [];
                afficherCreneauxPourDate(dateSelectionnee, creneauxPourDate);
            });
        });