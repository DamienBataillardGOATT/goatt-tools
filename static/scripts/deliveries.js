function enregistrerNote(commandeId) {
    var note = document.getElementById('note-' + commandeId).value;
    fetch('/deliveries/enregistrer-note/' + commandeId, {  
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