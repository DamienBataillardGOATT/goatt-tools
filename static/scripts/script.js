    var cart = [];

    var availableSlots = {}; // To store available time slots

    function updatePrice() {
        var selectElement = document.getElementById('string_id');
        var selectedOption = selectElement.options[selectElement.selectedIndex];
        var unitPrice = selectedOption.getAttribute('data-prix');
        var shopifyVariantId = selectedOption.getAttribute('data-shopify-variant-id');
        var quantity = document.getElementById('string_quantity').value;
        var totalPrice = unitPrice * quantity;
        document.getElementById('string_price').textContent = 'Prix: ' + totalPrice.toFixed(2) + ' €';
        document.getElementById('shopifyVariantId').value = shopifyVariantId;
    }

    // Add an event listener to the quantity field
    document.getElementById('string_quantity').addEventListener('change', updatePrice);

    // Update the initial price when the page loads
    document.addEventListener('DOMContentLoaded', function() {
        updatePrice();
    });

    function addToCart() {
        var selectElement = document.getElementById('string_id');
        var brand = selectElement.value;
        var price = selectElement.options[selectElement.selectedIndex].getAttribute('data-prix');
        var quantity = document.getElementById('string_quantity').value;
        var totalItem = price * quantity;

        cart.push({ brand: brand, quantity: quantity, price: price, totalItem: totalItem });
        displayCart();
    }

    function displayCart() {
        var cartList = document.getElementById('cartList');
        var cartTotal = document.getElementById('cartTotal');
        var inputTotalCartPrice = document.getElementById('totalCartPrice');
        var total = 0;

        cartList.innerHTML = '';

        cart.forEach(function(item, index) {
            var li = document.createElement('li');
            li.textContent = item.brand + ' x ' + item.quantity + ' : ' + item.totalItem + ' €';
            
            // Create a delete button
            var deleteButton = document.createElement('button');
            deleteButton.textContent = 'Supprimer';
            deleteButton.onclick = function() { removeFromCart(index); }; // Delete function
            li.appendChild(deleteButton);

            cartList.appendChild(li);

            total += parseFloat(item.totalItem);
        });

        cartTotal.textContent = total.toFixed(2);
        inputTotalCartPrice.value = total.toFixed(2);
    }

    function removeFromCart(index) {
        cart.splice(index, 1); // Remove the item from the array
        displayCart(); // Update the cart display
    }

    // Function to retrieve available slots and display them in the dropdown menu
    function retrieveAndDisplaySlots() {
        fetch('https://goatt-db.onrender.com/get_available_slots')
            .then(response => response.json())
            .then(data => {
                availableSlots = data; // Store the data
                const selectElement = document.getElementById('pickup_delivery_date');
                selectElement.innerHTML = ''; // Clear existing options

                // Loop through the data to add date options
                for (const date in data) {
                    const option = document.createElement('option');
                    option.value = date;
                    option.textContent = date;
                    selectElement.appendChild(option);
                }

                // Display slots for the first available date
                displaySlotsForDate();
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

        // Create a button for each time slot and break it down into hours
        slotsForDate.forEach(slot => {
            displayHoursForSlot(slot.trim(), selectedDate);
        });
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

    document.getElementById('store_pickup').addEventListener('change', function() {
        var storeAddress = this.options[this.selectedIndex].getAttribute('data-address');
        document.getElementById('store_address').value = storeAddress;
    });

    document.getElementById('store_delivery').addEventListener('change', function() {
        var storeAddress = this.options[this.selectedIndex].getAttribute('data-address');
        document.getElementById('store_delivery_address').value = storeAddress;
    });

    // Script to show/hide fields based on the chosen pickup option
    document.addEventListener('DOMContentLoaded', function() {
        var pickupOptions = document.querySelectorAll('input[name="pickup_option"]');
        pickupOptions.forEach(function(option) {
            option.addEventListener('change', function() {
                if (this.value === 'address') {
                    document.getElementById('pickup_address_container').style.display = 'block';
                    document.getElementById('store_pickup_container').style.display = 'none';
                } else if (this.value === 'store') {
                    document.getElementById('pickup_address_container').style.display = 'none';
                    document.getElementById('store_pickup_container').style.display = 'block';
                }
            });
        });

        var deliveryOptions = document.querySelectorAll('input[name="delivery_option"]');
        deliveryOptions.forEach(function(option) {
            option.addEventListener('change', function() {
                if (this.value === 'address') {
                    document.getElementById('delivery_address_container').style.display = 'block';
                    document.getElementById('store_delivery_container').style.display = 'none';
                } else if (this.value === 'store') {
                    document.getElementById('delivery_address_container').style.display = 'none';
                    document.getElementById('store_delivery_container').style.display = 'block';
                }
            });
        });
        
        // Retrieve and display available slots
        retrieveAndDisplaySlots();
        document.getElementById('pickup_delivery_date').addEventListener('change', function() {
            const selectedDate = this.value;
            const slotsForDate = availableSlots[selectedDate] || [];
            displaySlotsForDate(selectedDate, slotsForDate);
        });
    });
