let map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);
let marker;
async function predictRisk() {
    const country = document.getElementById('countrySelect').value;
    if (!country) {
        alert('Please select a country');
        return;
    }
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ country })
    });
    const data = await response.json();
    let resultHTML = `
        <h3>Risk Analysis for ${country}</h3>
        <br>
    `;
    for (const disaster in data.scores) {
        resultHTML += `
            <div class="result-card">
                <h4>${disaster}</h4>
                <p>Risk Score: ${data.scores[disaster]}</p>
            </div>
        `;
    }
    resultHTML += `
        <div class="highest-risk">
            Highest Risk: ${data.highest_disaster}
        </div>
    `;
    document.getElementById('results').innerHTML = resultHTML;
    // Update map
    map.setView([data.latitude, data.longitude], 5);
    if (marker) {
        map.removeLayer(marker);
    }
    marker = L.marker([data.latitude, data.longitude])
        .addTo(map)
        .bindPopup(`${country}<br>Highest Risk: ${data.highest_disaster}`)
        .openPopup();
}
async function getAdvice() {
    const country = document.getElementById('countrySelect').value;
    if (!country) {
        alert('Please select a country first');
        return;
    }
    const response = await fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ country })
    });
    const data = await response.json();
    document.getElementById('chatMessages').innerHTML = `
        <div class="chat-message">
            <strong>Emergency Advice:</strong><br><br>
            ${data.response}
            <br><br>
            <strong>Main Threat:</strong> ${data.highest_disaster}
        </div>
            `;
}
