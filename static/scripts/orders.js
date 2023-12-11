function enregistrerNote(commandeId) {
    var note = document.getElementById('note-' + commandeId).value;
    fetch('/orders/enregistrer-note/' + commandeId, {  
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

function verifierGlissement(commandeId, slider) {
    if (slider.value == '100') { 
        terminerCommande(commandeId, slider);
    }
}

function terminerCommande(commandeId, slider) {
    fetch('/orders/terminer-commande/' + commandeId, {  
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commandeElement = slider.closest('.commande');
            commandeElement.style.display = 'none'; 
        } else {
            slider.value = '0';  // Réinitialiser le slider en cas d'échec
            alert('Erreur lors de la mise à jour de la commande');
        }
    });
}
