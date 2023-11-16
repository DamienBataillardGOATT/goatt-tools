    var cart = [];

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

    // Function to retrieve available slots and display them in the dropdown menu
    function retrieveAndDisplaySlots() {
        fetch('https://goatt-db.onrender.com/get_available_slots')
            .then(response => response.json())
            .then(data => {
                availableSlots = data; // Store the data
                const selectElementDeposit = document.getElementById('pickup_deposit_date');
                const selectElementDelivery = document.getElementById('pickup_delivery_date');
                
                selectElementDeposit.innerHTML = '';
                selectElementDelivery.innerHTML = '';
    
                let firstDate = null;
    
                // Loop through the data to add date options
                for (const date in data) {
                    if (!firstDate) firstDate = date; // Store the first date
            
                    const europeanDate = convertToEuropeanDate(date);
                    const option = document.createElement('option');
                    option.value = date;
                    option.textContent = europeanDate;
                    selectElementDeposit.appendChild(option);
                }

                // Loop through the data to add date options
                for (const date in data) {
                    if (!firstDate) firstDate = date; // Store the first date
            
                    const europeanDate = convertToEuropeanDate(date);
                    const option = document.createElement('option');
                    option.value = date;
                    option.textContent = europeanDate;
                    selectElementDelivery.appendChild(option);
                }
    
                // Display slots for the first available date, if available
                if (firstDate) {
                    displaySlotsForDateDeposit(firstDate, data[firstDate]);
                    displaySlotsForDateDelivery(firstDate, data[firstDate])
                }
            })
            .catch(error => {
                console.error('Error retrieving available slots', error);
            });
    }

    
    function displaySlotsForDateDeposit(selectedDate, slotsForDate) {
        const selectElementDeposit = document.getElementById('pickup_time_dropdown');
        
        selectElementDeposit.innerHTML = ''; 
    
        if (slotsForDate) {
            slotsForDate.forEach(slot => {
                const option = document.createElement('option');
                option.value = `${selectedDate} ${slot}`;
                option.textContent = slot;
                selectElementDeposit.appendChild(option);
            });
        }
    }

    // Function to display time slot buttons for the selected date
    function displaySlotsForDateDelivery(selectedDate, slotsForDate) {
        const selectElementDelivery = document.getElementById('delevery_time_dropdown');

        selectElementDelivery.innerHTML = '';
    
        if (slotsForDate) {
            slotsForDate.forEach(slot => {
                const option = document.createElement('option');
                option.value = `${selectedDate} ${slot}`;
                option.textContent = slot;
                selectElementDelivery.appendChild(option);
            });
        }
    }

    function updateTimeSlotsDeposit() {
        const selectedDate_deposit = document.getElementById('pickup_deposit_date').value;
        const slotsForDate = availableSlots[selectedDate_deposit];
        if (slotsForDate) {
            displaySlotsForDateDeposit(selectedDate_deposit, slotsForDate);
        }
    }


    function updateTimeSlotsDelivery() {
        const selectedDate_delivery = document.getElementById('pickup_delivery_date').value;
        const slotsForDate = availableSlots[selectedDate_delivery];
        if (slotsForDate) {
            displaySlotsForDateDelivery(selectedDate_delivery, slotsForDate);
        }
    }

    function convertToEuropeanDate(date) {
        const [year, month, day] = date.split('-');
        return `${day}/${month}/${year}`;
    }

    function searchAddress(inputId, suggestionsId) {
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
                    };
                    suggestions.appendChild(div);
                });
            });
        }
    }

    // Script to show/hide fields based on the chosen pickup option
    document.addEventListener('DOMContentLoaded', function() {
        var pickupOptions = document.querySelectorAll('input[name="pickup_option"]');
        var deliveryOptions = document.querySelectorAll('input[name="delivery_option"]');
        const montantInput = document.getElementById('Montant');
        const traversInput = document.getElementById('Travers');
        const tensionInput = document.createElement('input');

        tensionInput.type = 'hidden';
        tensionInput.id = 'Tension';
        tensionInput.name = 'Tension';
        document.getElementById('orderForm').appendChild(tensionInput);

        function updateTensionValue() {
            let montant = montantInput.value.trim();
            let travers = traversInput.value.trim();
    
            if (montant === "recommandation expert" || travers === "recommandation expert") {
                tensionInput.value = "recommandation expert";
            } else if (montant === travers) {
                tensionInput.value = montant;
            } else {
                tensionInput.value = `${montant}-${travers}`;
            }
        }

        updatePrice();

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
        
        // Retrieve and display available slots
        retrieveAndDisplaySlots();

        document.getElementById('pickup_deposit_date').addEventListener('change', updateTimeSlotsDeposit);
        document.getElementById('pickup_delivery_date').addEventListener('change', updateTimeSlotsDelivery);

        montantInput.addEventListener('change', updateTensionValue);
        traversInput.addEventListener('change', updateTensionValue);
    });
