const speciesIcons = {
    'Iris Setosa': '🌿',
    'Iris Versicolor': '🌷',
    'Iris Virginica': '🌹'
};

const speciesColors = {
    'Iris Setosa': 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
    'Iris Versicolor': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    'Iris Virginica': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
};

const form = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const resultCard = document.getElementById('resultCard');
const speciesDisplay = document.getElementById('speciesDisplay');
const speciesName = document.getElementById('speciesName');
const speciesIcon = document.getElementById('speciesIcon');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceFill = document.getElementById('confidenceFill');
const probabilitiesList = document.getElementById('probabilitiesList');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    predictBtn.disabled = true;
    const originalBtnText = predictBtn.innerHTML;
    predictBtn.innerHTML = '<span class="loading"></span> Classifying...';
    
    const formData = {
        sepal_length: parseFloat(document.getElementById('sepal_length').value),
        sepal_width: parseFloat(document.getElementById('sepal_width').value),
        petal_length: parseFloat(document.getElementById('petal_length').value),
        petal_width: parseFloat(document.getElementById('petal_width').value)
    };
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + (data.error || 'Prediction failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = originalBtnText;
    }
});

function displayResults(data) {
    const { prediction, confidence, probabilities } = data;
    
    speciesName.textContent = prediction;
    speciesIcon.textContent = speciesIcons[prediction] || '🌸';
    
    confidenceValue.textContent = confidence.toFixed(2) + '%';
    confidenceFill.style.width = confidence + '%';
    confidenceFill.style.background = speciesColors[prediction] || confidenceFill.style.background;
    
    probabilitiesList.innerHTML = '';
    
    const sortedProbabilities = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1]);
    
    sortedProbabilities.forEach(([species, probability], index) => {
        const probabilityItem = document.createElement('div');
        probabilityItem.className = 'probability-item';
        
        if (index === 0) {
            probabilityItem.classList.add('highest');
        }
        
        probabilityItem.innerHTML = `
            <span class="probability-name">${species}</span>
            <span class="probability-value">${probability.toFixed(2)}%</span>
        `;
        
        probabilitiesList.appendChild(probabilityItem);
    });
    
    resultCard.style.display = 'block';
    
    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function resetForm() {
    form.reset();
    resultCard.style.display = 'none';
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

const inputs = document.querySelectorAll('input[type="number"]');
inputs.forEach(input => {
    input.addEventListener('input', function() {
        const value = parseFloat(this.value);
        
        this.style.borderColor = '';
        
        if (value <= 0) {
            this.style.borderColor = '#f5576c';
        } else if (value > 0) {
            this.style.borderColor = '#4ade80';
            setTimeout(() => {
                this.style.borderColor = '';
            }, 1000);
        }
    });
});

function fillSampleData(sample) {
    document.getElementById('sepal_length').value = sample[0];
    document.getElementById('sepal_width').value = sample[1];
    document.getElementById('petal_length').value = sample[2];
    document.getElementById('petal_width').value = sample[3];
}

window.addEventListener('load', async () => {
    try {
        const response = await fetch('/model-info');
        const data = await response.json();
        console.log('Model info:', data);
    } catch (error) {
        console.error('Error loading model info:', error);
    }
});

