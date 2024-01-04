    var availableSlots = {};

    var poseCordage = {
        brand: "Pose cordage",
        price: 14.99,
        quantity: 0, 
    };

    function searchString() {
        let input = document.getElementById('searchInput').value;
        input = input.toLowerCase();
        let suggestions = document.getElementById('suggestions');

        suggestions.innerHTML = '';

        if (input.length > 0) {
            for (let stringName in stringsInfo) {
                if (stringName.toLowerCase().includes(input)) {
                    let div = document.createElement('div');
                    document.getElementById('suggestions').style.display = 'block';
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

    function updatePrice() {
        var searchString = document.getElementById('searchInput').value;
        var info = stringsInfo[searchString];
        if (info) {
            var unitPrice = info.prix;
            var shopifyVariantId = info.shopify_variant_id;
            var quantityElement = document.getElementById('string_quantity');
            var quantity = parseInt(quantityElement.value, 10);
    
            if (!Number.isInteger(quantity)) {
                quantity = Math.round(quantity); 
                quantityElement.value = quantity; 
            }
    
            var totalPrice = unitPrice * quantity;
            var poseCordagePrice = 14.99; 
            totalPrice += poseCordagePrice;
    
            document.getElementById('string_price').textContent = totalPrice.toFixed(2) + ' €';
            document.getElementById('shopifyVariantId').value = shopifyVariantId;
            document.getElementById('totalPrice').value = totalPrice.toFixed(2);
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
                    document.getElementById('emailSuggestions').style.display = 'block';
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
                    updatePrice();
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

    function extractFirstTwoCharacters(timeSlot) {
        return timeSlot.substring(0, 2);
    }

    function addDaysToDate(date, days) {
        var result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }

    function retrieveAndDisplaySlots() {
        fetch('https://goatt-db.onrender.com/get_available_slots')
            .then(response => response.json())
            .then(data => {
                availableSlots = data;
                const selectElementDeposit = document.getElementById('pickup_deposit_date');
                const selectElementDelivery = document.getElementById('pickup_delivery_date');
                
                selectElementDeposit.innerHTML = '';
                selectElementDelivery.innerHTML = '';
        
                for (const date in data) {
                    const europeanDate = convertToEuropeanDate(date);
                    const optionDeposit = document.createElement('option');
                    const optionDelivery = document.createElement('option');
    
                    optionDeposit.value = date;
                    optionDeposit.textContent = europeanDate;
                    selectElementDeposit.appendChild(optionDeposit);
    
                    optionDelivery.value = date;
                    optionDelivery.textContent = europeanDate;
                    selectElementDelivery.appendChild(optionDelivery);
                }
    
                if (Object.keys(data).length > 0) {
                    let firstDate = Object.keys(data)[0];
                    displaySlotsForDateDeposit(firstDate, data[firstDate]);
                    displaySlotsForDateDelivery(firstDate, data[firstDate]);
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

        updateDeliveryDates(selectedDateDeposit);

    }

    function updateDeliveryDates(startDate) {
        const selectElementDelivery = document.getElementById('pickup_delivery_date');
        selectElementDelivery.innerHTML = '';
    
        for (const date in availableSlots) {
            let currentDate = new Date(date);
            let startDateObj = new Date(startDate);
            if (currentDate >= startDateObj) {
                let europeanDate = convertToEuropeanDate(date);
                const option = document.createElement('option');
                option.value = date;
                option.textContent = europeanDate;
                selectElementDelivery.appendChild(option);
            }
        }
    
        displaySlotsForDateDelivery(startDate, availableSlots[startDate]);
    }

    function convertToEuropeanDate(date) {
        const [year, month, day] = date.split('-');
        const dateObj = new Date(year, month - 1, day); 

        const options = { weekday: 'long', day: 'numeric', month: 'long' };

        return dateObj.toLocaleDateString('fr-FR', options);
    }
    
    function searchAddressDeposit(inputId, suggestionsId) {
        var input = document.getElementById(inputId).value;
        console.log(encodeURIComponent(input))
    
        if (input.length > 2) {
            fetch('https://api-adresse.data.gouv.fr/search/?q=' + encodeURIComponent(input))
            .then(response => {
                if (!response.ok) {
                    throw new Error('Réponse réseau non OK');
                }
                return response.json();
            })
            .then(data => {
                var suggestions = document.getElementById(suggestionsId);
                suggestions.innerHTML = '';
                data.features.forEach(function(feature) {
                    var div = document.createElement('div');
                    div.innerHTML = feature.properties.label;
                    div.onclick = function() {
                        var selectedAddress = feature.properties.label;
    
                        document.getElementById(inputId).value = selectedAddress;
    
                        document.getElementById('delivery_address').value = selectedAddress;
    
                        suggestions.innerHTML = '';
    
                        var longitude = feature.geometry.coordinates[0];
                        var latitude = feature.geometry.coordinates[1];
    
                        document.getElementById('longitudeDeposit').value = longitude;
                        document.getElementById('latitudeDeposit').value = latitude;
    
                        document.getElementById('longitudeDelivery').value = longitude;
                        document.getElementById('latitudeDelivery').value = latitude;
                    };
                    suggestions.appendChild(div);
                });
            })
            .catch(error => {
                console.error('Problème de récupération des données :', error);
                var suggestions = document.getElementById(suggestionsId);
                suggestions.innerHTML = 'Impossible de charger les suggestions.';
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

    document.addEventListener('DOMContentLoaded', function() {
        var pickupOptions = document.querySelectorAll('input[name="pickup_option"]');
        var deliveryOptions = document.querySelectorAll('input[name="delivery_option"]');
        var inputs = document.getElementsByTagName('input');

        // Add an event listener to the quantity field
        document.getElementById('string_quantity').addEventListener('change', updatePrice);

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
                    var pickupField = document.getElementById('pickup_address');
                    if (this.value === 'address') {
                        document.getElementById('pickup_address_container').style.display = 'flex';
                        document.getElementById('pickup_time_dropdown').style.display = 'flex';
                        pickupField.required = true;
                    } else if (this.value === 'store') {
                        document.getElementById('pickup_address_container').style.display = 'none';
                        document.getElementById('pickup_time_dropdown').style.display = 'none';
                        pickupField.required = false;
                    }
                });
            });

            deliveryOptions.forEach(function(option) {
                option.addEventListener('change', function() {
                    var deliveryField = document.getElementById('delivery_address');
                    if (this.value === 'address') {
                        document.getElementById('delivery_address_container').style.display = 'flex';
                        document.getElementById('delivery_time_dropdown').style.display = 'flex';
                        deliveryField.required = true;
                    } else if (this.value === 'store') {
                        document.getElementById('delivery_address_container').style.display = 'none';
                        document.getElementById('delivery_time_dropdown').style.display = 'none'
                        deliveryField.required = false;
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
