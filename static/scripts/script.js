    var availableSlots = {}; // To store available time slots

    var poseCordage = {
        brand: "Pose cordage",
        price: 14.99,
        quantity: 0, 
    };
    
    function searchRaquette() {
        let input = document.getElementById('searchInput').value;
        input = input.toLowerCase();
        let suggestions = document.getElementById('suggestions');
    
        suggestions.innerHTML = '';
    
        if (input.length > 0) {
            for (let stringName in stringsInfo) {
                if (stringName.toLowerCase().includes(input)) {
                    let div = document.createElement('div');
                    div.innerHTML = stringName;
                    div.onclick = function() {
                        document.getElementById('searchInput').value = stringName;
                        suggestions.innerHTML = '';
                    };
                    suggestions.appendChild(div);
                }
            }
        }
    }

    function searchEmail() {
        let input = document.getElementById('search_email').value;
        input = input.toLowerCase();
        let suggestions = document.getElementById('emailSuggestions');
    
        suggestions.innerHTML = '';
    
        if (input.length > 0) {
            emailsInfo.forEach(email => {
                if (email.toLowerCase().includes(input)) {
                    let div = document.createElement('div');
                    div.innerHTML = email;
                    div.onclick = function() {
                        document.getElementById('search_email').value = email;
                        suggestions.innerHTML = '';
                        searchClientWithEmail(email);
                    };
                    suggestions.appendChild(div);
                }
            });
        }
    }
    
    function searchClientWithEmail(email) {
        fetch('/client/search_client', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'search_email=' + encodeURIComponent(email)
        })
        .then(response => response.json())
        .then(data => {
            if (data.found) {
                let clientData = data.client;

                if (data.cordage) {
                    document.getElementById('searchInput').value = data.cordage;
                }
                if (data.tension) {
                    document.getElementById('Tension').value = data.tension;
                }

                document.getElementById('phonenumber').value = data.phonenumber || '';
                document.getElementById('name').value = clientData.Nom || '';
                document.getElementById('firstname').value = clientData.Prénom || '';
            }
        });
    }

    function updatePrice() {
        var searchString = document.getElementById('searchInput').value;
        var info = stringsInfo[searchString];
        if (info) {
            var unitPrice = info.prix;
            var shopifyVariantId = info.shopify_variant_id;
            var quantity = document.getElementById('string_quantity').value;
            var totalPrice = unitPrice * quantity;
    
            var poseCordagePrice = 14.99; 
            totalPrice += poseCordagePrice;
    
            document.getElementById('string_price').textContent = totalPrice.toFixed(2) + ' €';
            document.getElementById('shopifyVariantId').value = shopifyVariantId;
            document.getElementById('totalPrice').value = totalPrice.toFixed(2);
        }
    }
    
    // Add an event listener to the quantity field
    document.getElementById('string_quantity').addEventListener('change', updatePrice);

    function extractFirstTwoCharacters(timeSlot) {
        return timeSlot.substring(0, 2);
    }

    // Fonction pour ajouter des jours à une date
    function addDaysToDate(date, days) {
        var result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }

    // Fonction pour convertir une date en format européen
    function convertToEuropeanDate(date) {
        return date.split('-').reverse().join('/');
    }

    // Fonction pour récupérer et afficher les créneaux disponibles
    function retrieveAndDisplaySlots() {
        fetch('https://goatt-db.onrender.com/get_available_slots')
            .then(response => response.json())
            .then(data => {
                availableSlots = data; // Stocker les données
                const selectElementDeposit = document.getElementById('pickup_deposit_date');
                const selectElementDelivery = document.getElementById('pickup_delivery_date');
                
                selectElementDeposit.innerHTML = '';
                selectElementDelivery.innerHTML = '';
        
                let firstDate = null;
        
                // Boucle pour ajouter des options de date de dépôt
                for (const date in data) {
                    if (!firstDate) firstDate = date; // Stocker la première date
            
                    const europeanDate = convertToEuropeanDate(date);
                    const option = document.createElement('option');
                    option.value = date;
                    option.textContent = europeanDate;
                    selectElementDeposit.appendChild(option);
                }

                // Calculer la première date de livraison (2 jours après la première date de dépôt)
                if (firstDate) {
                    let firstDeliveryDate = addDaysToDate(new Date(firstDate), 2);

                    // Boucle pour ajouter des options de date de livraison
                    for (const date in data) {
                        let currentDate = new Date(date);
                        if (currentDate >= firstDeliveryDate) {
                            let europeanDate = convertToEuropeanDate(date);
                            const option = document.createElement('option');
                            option.value = date;
                            option.textContent = europeanDate;
                            selectElementDelivery.appendChild(option);
                        }
                    }

                    displaySlotsForDateDeposit(firstDate, data[firstDate]);
                    // Afficher les créneaux pour la première date de livraison disponible
                    let firstDeliveryDateFormatted = firstDeliveryDate.toISOString().split('T')[0];
                    displaySlotsForDateDelivery(firstDeliveryDateFormatted, data[firstDeliveryDateFormatted]);
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des créneaux disponibles', error);
            });
    }

    
    function displaySlotsForDateDeposit(selectedDate, slotsForDate) {
        const selectElementDeposit = document.getElementById('pickup_time_dropdown');
        
        selectElementDeposit.innerHTML = ''; 
    
        if (slotsForDate && slotsForDate.length > 0) {
            slotsForDate.forEach(slot => {
                const option = document.createElement('option');
                option.value = `${slot}`;
                option.textContent = slot;
                selectElementDeposit.appendChild(option);
            });
    
            var firstSlot = slotsForDate[0];
            var firstTwoChars = extractFirstTwoCharacters(firstSlot);
            document.getElementById('selected_slot_deposit').value = firstTwoChars;
        }
    }

    function displaySlotsForDateDelivery(selectedDate, slotsForDate) {
        const selectElementDelivery = document.getElementById('delivery_time_dropdown');

        selectElementDelivery.innerHTML = '';
    
        if (slotsForDate && slotsForDate.length > 0) {
            slotsForDate.forEach(slot => {
                const option = document.createElement('option');
                option.value = `${slot}`;
                option.textContent = slot;
                selectElementDelivery.appendChild(option);
            });

            var firstSlot = slotsForDate[0];
            var firstTwoChars = extractFirstTwoCharacters(firstSlot);
            document.getElementById('selected_slot_delivery').value = firstTwoChars;
        }
    }

    function updateTimeSlotsDeposit() {
        const selectedDateDeposit = document.getElementById('pickup_deposit_date').value;
        const slotsForDate = availableSlots[selectedDateDeposit];
        if (slotsForDate) {
            displaySlotsForDateDeposit(selectedDateDeposit, slotsForDate);
        }

        let newDeliveryDate = addDaysToDate(new Date(selectedDateDeposit), 2);
        updateDeliveryDates(newDeliveryDate);
    }

    function updateDeliveryDates(newDeliveryDate) {
        const selectElementDelivery = document.getElementById('pickup_delivery_date');
        selectElementDelivery.innerHTML = '';
    
        for (const date in availableSlots) {
            let currentDate = new Date(date);
            if (currentDate >= newDeliveryDate) {
                let europeanDate = convertToEuropeanDate(date);
                const option = document.createElement('option');
                option.value = date;
                option.textContent = europeanDate;
                selectElementDelivery.appendChild(option);
            }
        }
    
        let firstDeliveryDateFormatted = newDeliveryDate.toISOString().split('T')[0];
        displaySlotsForDateDelivery(firstDeliveryDateFormatted, availableSlots[firstDeliveryDateFormatted]);
    }

    function convertToEuropeanDate(date) {
        const [year, month, day] = date.split('-');
        return `${day}/${month}/${year}`;
    }

    function searchAddressDeposit(inputId, suggestionsId) {
        var input = document.getElementById(inputId).value;

        if (input.length > 2) {
            fetch('https://api-adresse.data.gouv.fr/search/?q=' + encodeURIComponent(input))
            .then(response => response.json())
            .then(data => {
                var suggestions = document.getElementById(suggestionsId);
                suggestions.innerHTML = '';
                data.features.forEach(function(feature) {
                    var div = document.createElement('div');
                    div.innerHTML = feature.properties.label;
                    div.onclick = function() {
                        document.getElementById(inputId).value = feature.properties.label;
                        suggestions.innerHTML = '';

                        var longitudeDeposit = feature.geometry.coordinates[0];
                        var latitudeDeposit = feature.geometry.coordinates[1];

                        document.getElementById('longitudeDeposit').value = longitudeDeposit;
                        document.getElementById('latitudeDeposit').value = latitudeDeposit;
                    };
                    suggestions.appendChild(div);
                });
            });
        }
    }

    function searchAddressDelivery(inputId, suggestionsId) {
        var input = document.getElementById(inputId).value;

        if (input.length > 2) {
            fetch('https://api-adresse.data.gouv.fr/search/?q=' + encodeURIComponent(input))
            .then(response => response.json())
            .then(data => {
                var suggestions = document.getElementById(suggestionsId);
                suggestions.innerHTML = '';
                data.features.forEach(function(feature) {
                    var div = document.createElement('div');
                    div.innerHTML = feature.properties.label;
                    div.onclick = function() {
                        document.getElementById(inputId).value = feature.properties.label;
                        suggestions.innerHTML = '';

                        var longitudeDelivery = feature.geometry.coordinates[0];
                        var latitudeDelivery = feature.geometry.coordinates[1];

                        document.getElementById('longitudeDelivery').value = longitudeDelivery;
                        document.getElementById('latitudeDelivery').value = latitudeDelivery;
                    };
                    suggestions.appendChild(div);
                });
            });
        }
    }

    function updateTensionValue() {
        let tensionInput = document.getElementById('Tension');
        let tensionValue = tensionInput.value.trim();
    
        if (tensionValue.toLowerCase() === "recommandation expert") {
            tensionInput.value = "recommandation expert";
        } else {
            let tensions = tensionValue.split(',').map(t => t.trim());
            if (tensions.length === 2 && tensions[0] !== tensions[1]) {
                tensionInput.value = `${tensions[0]}-${tensions[1]}`;
            }
        }
    }


    // Script to show/hide fields based on the chosen pickup option
    document.addEventListener('DOMContentLoaded', function() {
        var pickupOptions = document.querySelectorAll('input[name="pickup_option"]');
        var deliveryOptions = document.querySelectorAll('input[name="delivery_option"]');
        var inputs = document.getElementsByTagName('input');

        updatePrice();

        for (var i = 0; i < inputs.length; i++) {
            inputs[i].onkeydown = function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    return false;
                }
            }
        }

        pickupOptions.forEach(function(option) {
            option.addEventListener('change', function() {
                var pickupTimeField = document.getElementById('pickup_time');
                if (this.value === 'address') {
                    document.getElementById('pickup_address_container').style.display = 'block';
                    document.getElementById('store_pickup_address').value = '';
                    document.getElementById('pickup_time_container').style.display = 'block';
                    pickupTimeField.required = true;
                } else if (this.value === 'store') {
                    document.getElementById('pickup_address_container').style.display = 'none';
                    document.getElementById('pickup_time_container').style.display = 'none';
                    pickupTimeField.required = false;
                }
            });
        });

        deliveryOptions.forEach(function(option) {
            option.addEventListener('change', function() {
                if (this.value === 'address') {
                    document.getElementById('delivery_address_container').style.display = 'block';
                    document.getElementById('store_delivery_address').value = '';
                    document.getElementById('delevery_time_container').style.display = 'block';
                } else if (this.value === 'store') {
                    document.getElementById('delivery_address_container').style.display = 'none';
                    document.getElementById('delevery_time_container').style.display = 'none'
                }
            });
        });
        
        retrieveAndDisplaySlots();

        document.getElementById('pickup_deposit_date').addEventListener('change', updateTimeSlotsDeposit);
        document.getElementById('pickup_time_dropdown').addEventListener('change', function() {
            var selectedSlot = this.value;
            var firstTwoChars = extractFirstTwoCharacters(selectedSlot);
            document.getElementById('selected_slot_deposit').value = firstTwoChars;
        });

        document.getElementById('delivery_time_dropdown').addEventListener('change', function() {
            var selectedSlot = this.value;
            var firstTwoChars = extractFirstTwoCharacters(selectedSlot);
            document.getElementById('selected_slot_delivery').value = firstTwoChars;
        });

        document.getElementById('Tension').addEventListener('change', updateTensionValue);

    });
