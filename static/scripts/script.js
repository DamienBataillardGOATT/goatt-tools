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
                const selectElement = document.getElementById('pickup_delivery_date');
                selectElement.innerHTML = ''; // Clear existing options
    
                let firstDate = null;
    
                // Loop through the data to add date options
                for (const date in data) {
                    if (!firstDate) firstDate = date; // Store the first date
    
                    const option = document.createElement('option');
                    option.value = date;
                    option.textContent = date;
                    selectElement.appendChild(option);
                }
    
                // Display slots for the first available date, if available
                if (firstDate) {
                    displaySlotsForDate(firstDate, data[firstDate]);
                }
            })
            .catch(error => {
                console.error('Error retrieving available slots', error);
            });
    }

    // Function to break down slots into individual hours and create buttons for each hour
    function displayHoursForSlot(slot, date) {
        const hours = slot.split('-'); // Example: "10h - 12h" becomes ["10h ", " 12h"]
        const startHour = parseInt(hours[0]); // Example: "10h " becomes 10
        const endHour = parseInt(hours[1]); // Example: " 12h" becomes 12
        const container = document.getElementById('timeSlotsContainer');

        // Create a button for each hour in the interval, including the end hour
        for (let hour = startHour; hour <= endHour; hour++) {
            const button = document.createElement('button');
            button.type = 'button'; // Make sure to set the type to 'button'
            button.textContent = `${hour}h`; // Example: "10h"
            button.value = `${date} ${hour}h`;
            button.classList.add('slot-btn'); // Add a class for styling
            button.onclick = function(event) {
                event.preventDefault(); // Prevent form submission
                chooseSlot(this.value);
            };
            container.appendChild(button);
        }
    }

    // Function to display time slot buttons for the selected date
    function displaySlotsForDate(selectedDate, slotsForDate) {
        const container = document.getElementById('timeSlotsContainer');
        container.innerHTML = '';
    
        if (slotsForDate) {
            slotsForDate.forEach(slot => {
                displayHoursForSlot(slot.trim(), selectedDate);
            });
        }
    }

    function extractHour(slot) {
        // Use a regular expression to find the digits before the 'h'
        const result = slot.match(/(\d+)h/);

        // Check if the result is not null and return the first captured group
        if (result && result[1]) {
            return parseInt(result[1], 10); // Convert the result to a number
        } else {
            console.error('Invalid slot format');
            return null; // or you can return a default value or throw an error
        }
    }

    // Function to handle the selection of a time slot
    function chooseSlot(hour) {
        console.log('Selected hour:', hour);
        const hourWithoutDate = extractHour(hour);
        // Update the hidden field with the value of the selected hour
        document.getElementById('selected_slot').value = hourWithoutDate;
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
        var storeAddress = "174 Quai de Jemmapes, 75010 Paris, France"; 
        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); // Janvier est 0 !
        var yyyy = today.getFullYear();

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
        today = yyyy + '-' + mm + '-' + dd;
        document.getElementById('deposit_date').value = today;
        });

        deliveryOptions.forEach(function(option) {
            option.addEventListener('change', function() {
                if (this.value === 'address') {
                    document.getElementById('delivery_address_container').style.display = 'block';
                    document.getElementById('store_delivery_address').value = '';
                } else if (this.value === 'store') {
                    document.getElementById('delivery_address_container').style.display = 'none';
                }
            });
        });
        
        // Retrieve and display available slots
        retrieveAndDisplaySlots();

        document.getElementById('pickup_delivery_date').onchange = function() {
            const selectedDate = this.value;
            const slotsForDate = availableSlots[selectedDate];
            if (slotsForDate) {
                displaySlotsForDate(selectedDate, slotsForDate);
            }
        };
    });
