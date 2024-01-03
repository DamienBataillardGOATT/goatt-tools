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

function checkSlide(commandeId, slider, isFinal) {
    const value = slider.value;
    slider.style.background = `linear-gradient(to right, #4CAF50 ${value}%, #d3d3d3 ${value}%)`;

    if (isFinal && value === '100') {
        finishCommande(commandeId, slider);
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

function openModal(commandeDetailsJson, categorie) {
    console.log("JSON reçu:", commandeDetailsJson);
    var commandeDetails = JSON.parse(commandeDetailsJson);

    var infoCategorieHtml = '';

    switch (categorie) {
        case 'aRecuperer':
            break;
        case 'aCorder':
            infoCategorieHtml = `<textarea id="note-${commandeDetails.id}" onblur="writeNote('${commandeDetails.id}')"placeholder="Ajoutez une note ici...">${commandeDetails.note}</textarea>
                                <div class="slider-container">
                                    <input type="range" min="0" max="100" value="0" class="slider" id="slider-${commandeDetails.id}" oninput="checkSlide('${commandeDetails.id}', this)">
                                    <div class="slider-value" id="slider-text-${commandeDetails.id}">Pose terminée</div>
                                </div>`;
            break;
        case 'aLivrer':
            break;
    }
    
    var modalContentHtml = `
    <p><strong>${commandeDetails.date_livraison} ${commandeDetails.heure_livraison}</strong></p>
    ${commandeDetails.type == 'B2C' ? 
        `<p><strong>${commandeDetails.client}</strong> (${commandeDetails.telephone})</p>` : 
         `<p><strong>ID Client: ${commandeDetails.id_client}</strong></p>`}
    <p><strong>Nombre de raquettes:</strong> ${commandeDetails.quantite}</p>
    <p><strong>Tension:</strong> ${commandeDetails.tension}</p>
    <strong>Articles:</strong>
    <div>${commandeDetails.articles.map(article => `<div class="article">${article}</div>`).join('')}</div>
    <a href="${commandeDetails.shopify_url}">${commandeDetails.shopify_url}</a>
    ${infoCategorieHtml}`;
    
    document.getElementById('modalDetails').innerHTML = modalContentHtml;
    document.getElementById('myModal').style.display = 'block';

    const slider = document.getElementById(`slider-${commandeDetails.id}`);
    if (slider) {
        slider.oninput = function() { checkSlide(commandeDetails.id, this, false); };
        slider.onchange = function() { checkSlide(commandeDetails.id, this, true); };
    }
}

function closeModal() {
  document.getElementById('myModal').style.display = 'none';
}

window.onclick = function(event) {
  if (event.target == document.getElementById('myModal')) {
    closeModal();
  }
}