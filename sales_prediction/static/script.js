const form = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const resultCard = document.getElementById('resultCard');
const formGrid = document.getElementById('formGrid');
const predictionValue = document.getElementById('predictionValue');
const featuresUsed = document.getElementById('featuresUsed');

let featureInfo = [];

window.addEventListener('load', async () => {
    try {
        const response = await fetch('/model-info');
        const data = await response.json();
        
        if (data.features && data.feature_info) {
            featureInfo = data.feature_info;
            createFormFields(data.feature_info);
        }
    } catch (error) {
        console.error('Error loading model info:', error);
    }
});

function createFormFields(features) {
    formGrid.innerHTML = '';
    
    features.forEach(feature => {
        const inputGroup = document.createElement('div');
        inputGroup.className = 'input-group';
        
        const label = document.createElement('label');
        label.setAttribute('for', feature.name.toLowerCase().replace(' ', '_'));
        label.innerHTML = `<span class="label-icon">📢</span> ${feature.name}`;
        
        const input = document.createElement('input');
        input.type = 'number';
        input.id = feature.name.toLowerCase().replace(' ', '_');
        input.name = feature.name.toLowerCase().replace(' ', '_');
        input.step = '0.1';
        input.min = '0';
        input.required = true;
        input.placeholder = `Range: ${feature.min.toFixed(1)} - ${feature.max.toFixed(1)}`;
        input.value = '';
        
        inputGroup.appendChild(label);
        inputGroup.appendChild(input);
        formGrid.appendChild(inputGroup);
    });
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    predictBtn.disabled = true;
    const originalBtnText = predictBtn.innerHTML;
    predictBtn.innerHTML = '<span class="loading"></span> Predicting...';
    
    const formData = {};
    featureInfo.forEach(feature => {
        const inputId = feature.name.toLowerCase().replace(' ', '_');
        const input = document.getElementById(inputId);
        if (input) {
            const value = parseFloat(input.value);
            formData[feature.name] = isNaN(value) ? 0 : value;
        }
    });
    
    console.log('Sending prediction request:', formData);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        console.log('Prediction response:', data);
        
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
    const { prediction, features } = data;
    
    if (!prediction && prediction !== 0) {
        console.error('No prediction value in response:', data);
        alert('Error: No prediction value received');
        return;
    }
    
    predictionValue.textContent = '₹' + parseFloat(prediction).toFixed(2);
    
    featuresUsed.innerHTML = '<h4>Input Values</h4>';
    const featuresList = document.createElement('div');
    featuresList.className = 'features-list';
    
    Object.entries(features).forEach(([key, value]) => {
        const featureItem = document.createElement('div');
        featureItem.className = 'feature-item';
        featureItem.innerHTML = `
            <span class="feature-name">${key}</span>
            <span class="feature-value">₹${parseFloat(value).toFixed(2)}</span>
        `;
        featuresList.appendChild(featureItem);
    });
    
    featuresUsed.appendChild(featuresList);
    
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '20px';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.gap = '15px';
    buttonContainer.style.flexDirection = 'column';
    
    const viewBtn = document.createElement('button');
    viewBtn.className = 'export-btn';
    viewBtn.innerHTML = '<span class="btn-text">📊 View All Predictions</span>';
    viewBtn.onclick = () => {
        window.open('/exports', '_blank');
    };
    
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'export-btn';
    downloadBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
    downloadBtn.innerHTML = '<span class="btn-text">📥 Download Predictions (CSV)</span>';
    downloadBtn.onclick = () => {
        window.location.href = '/download-predictions';
    };
    
    buttonContainer.appendChild(viewBtn);
    buttonContainer.appendChild(downloadBtn);
    featuresUsed.appendChild(buttonContainer);
    
    resultCard.style.display = 'block';
    
    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function resetForm() {
    form.reset();
    resultCard.style.display = 'none';
    
    featureInfo.forEach(feature => {
        const inputId = feature.name.toLowerCase().replace(' ', '_');
        const input = document.getElementById(inputId);
        if (input) {
            input.value = '';
        }
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

const inputs = document.querySelectorAll('input[type="number"]');
inputs.forEach(input => {
    input.addEventListener('input', function() {
        const value = parseFloat(this.value);
        this.style.borderColor = '';
        
        if (value < 0) {
            this.style.borderColor = '#f5576c';
        } else if (value > 0) {
            this.style.borderColor = '#4ade80';
            setTimeout(() => {
                this.style.borderColor = '';
            }, 1000);
        }
    });
});
