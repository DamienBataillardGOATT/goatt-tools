function writeNote(commandeId) {
    var note = document.getElementById('note-' + commandeId).value;
    fetch('/orders/writeNote/' + commandeId, {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ note: note })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            console.log('Note enregistrée');
        } else {
            console.error("Erreur lors de l'enregistrement de la note");
        }
    });
}

function checkSlide(commandeId, slider) {
    const sliderText = document.getElementById(`slider-text-${commandeId}`);
    const value = slider.value;


    slider.style.background = `linear-gradient(to right, #4CAF50 ${value}%, #d3d3d3 ${value}%)`;

    if (value === '100') {
        sliderText.style.display = 'block'; 
        sliderText.textContent = 'Pose terminée';
        finishCommande(commandeId, slider);
    } else {
        sliderText.style.display = 'none'; 
    }
}

function finishCommande(commandeId, slider) {
    fetch(`/orders/finishCommande/${commandeId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commandeElement = slider.closest('.commandes');
            commandeElement.style.display = 'none';
        } else {
            slider.value = '0';
            document.getElementById(`slider-text-${commandeId}`).textContent = 'Pose à faire';
            slider.style.background = 'linear-gradient(to right, #4CAF50 0%, #d3d3d3 0%)';
            alert('Erreur lors de la mise à jour de la commande.');
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
        slider.value = '0';
        document.getElementById(`slider-text-${commandeId}`).textContent = 'Pose à faire';
        slider.style.background = 'linear-gradient(to right, #4CAF50 0%, #d3d3d3 0%)';
        alert('Erreur réseau lors de la mise à jour de la commande.');
    });
}