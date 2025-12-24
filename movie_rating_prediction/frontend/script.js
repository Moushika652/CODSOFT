document.getElementById('prediction-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const genres = document.getElementById('genres').value.split(',').map(g => g.trim());
    const director = document.getElementById('director').value;
    const actors = document.getElementById('actors').value.split(',').map(a => a.trim());
    const runtime = parseInt(document.getElementById('runtime').value);
    const release_year = parseInt(document.getElementById('release_year').value);
    const vote_count = parseInt(document.getElementById('vote_count').value);

    const requestData = {
        genres,
        director,
        actors,
        runtime,
        release_year,
        vote_count
    };

    try {
        const response = await fetch('http://localhost:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Failed to fetch prediction');
        }

        const data = await response.json();

        document.getElementById('predicted-rating').textContent = `Predicted Rating: ${data.predicted_rating}`;
        document.getElementById('confidence-range').textContent = `Confidence Range: ${data.confidence_range}`;

        const featuresList = document.getElementById('influencing-features');
        featuresList.innerHTML = '';
        data.top_influencing_features.forEach(feature => {
            const listItem = document.createElement('li');
            listItem.textContent = feature;
            featuresList.appendChild(listItem);
        });
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while fetching the prediction.');
    }
});