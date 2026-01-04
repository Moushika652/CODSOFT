// Species icon mapping
const speciesIcons = {
    'Iris Setosa': '🌿',
    'Iris Versicolor': '🌷',
    'Iris Virginica': '🌹'
};

// Species color mapping
const speciesColors = {
    'Iris Setosa': 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
    'Iris Versicolor': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    'Iris Virginica': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
};

// DOM Elements
const form = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const resultCard = document.getElementById('resultCard');
const speciesDisplay = document.getElementById('speciesDisplay');
const speciesName = document.getElementById('speciesName');
const speciesIcon = document.getElementById('speciesIcon');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceFill = document.getElementById('confidenceFill');
const probabilitiesList = document.getElementById('probabilitiesList');

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Disable button and show loading
    predictBtn.disabled = true;
    const originalBtnText = predictBtn.innerHTML;
    predictBtn.innerHTML = '<span class="loading"></span> Classifying...';
    
    // Get form data
    const formData = {
        sepal_length: parseFloat(document.getElementById('sepal_length').value),
        sepal_width: parseFloat(document.getElementById('sepal_width').value),
        petal_length: parseFloat(document.getElementById('petal_length').value),
        petal_width: parseFloat(document.getElementById('petal_width').value)
    };
    
    try {
        // Make prediction request
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display results
            displayResults(data);
        } else {
            // Show error
            alert('Error: ' + (data.error || 'Prediction failed'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        // Re-enable button
        predictBtn.disabled = false;
        predictBtn.innerHTML = originalBtnText;
    }
});

// Display prediction results
function displayResults(data) {
    const { prediction, confidence, probabilities } = data;
    
    // Update species display
    speciesName.textContent = prediction;
    speciesIcon.textContent = speciesIcons[prediction] || '🌸';
    
    // Update confidence
    confidenceValue.textContent = confidence.toFixed(2) + '%';
    confidenceFill.style.width = confidence + '%';
    confidenceFill.style.background = speciesColors[prediction] || confidenceFill.style.background;
    
    // Update probabilities
    probabilitiesList.innerHTML = '';
    
    // Sort probabilities by value (highest first)
    const sortedProbabilities = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1]);
    
    sortedProbabilities.forEach(([species, probability], index) => {
        const probabilityItem = document.createElement('div');
        probabilityItem.className = 'probability-item';
        
        // Highlight the highest probability
        if (index === 0) {
            probabilityItem.classList.add('highest');
        }
        
        probabilityItem.innerHTML = `
            <span class="probability-name">${species}</span>
            <span class="probability-value">${probability.toFixed(2)}%</span>
        `;
        
        probabilitiesList.appendChild(probabilityItem);
    });
    
    // Show result card with animation
    resultCard.style.display = 'block';
    
    // Scroll to result
    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Reset form function
function resetForm() {
    form.reset();
    resultCard.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Add input validation and real-time feedback
const inputs = document.querySelectorAll('input[type="number"]');
inputs.forEach(input => {
    input.addEventListener('input', function() {
        const value = parseFloat(this.value);
        
        // Remove any previous error styling
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

// Add sample data buttons (optional enhancement)
function fillSampleData(sample) {
    document.getElementById('sepal_length').value = sample[0];
    document.getElementById('sepal_width').value = sample[1];
    document.getElementById('petal_length').value = sample[2];
    document.getElementById('petal_width').value = sample[3];
}

// Initialize - check if model is ready
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/model-info');
        const data = await response.json();
        console.log('Model info:', data);
    } catch (error) {
        console.error('Error loading model info:', error);
    }
});

