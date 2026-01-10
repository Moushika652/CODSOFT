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
        input.max = feature.max * 2; // Allow some flexibility
        input.required = true;
        input.placeholder = `Range: ${feature.min.toFixed(1)} - ${feature.max.toFixed(1)}`;
        input.value = '';
        
        // Add validation message container
        const validationMsg = document.createElement('span');
        validationMsg.className = 'validation-message';
        validationMsg.style.display = 'none';
        
        // Enhanced validation
        input.addEventListener('input', function() {
            validateInput(this, feature, validationMsg);
        });
        
        input.addEventListener('blur', function() {
            validateInput(this, feature, validationMsg);
        });
        
        inputGroup.appendChild(label);
        inputGroup.appendChild(input);
        inputGroup.appendChild(validationMsg);
        formGrid.appendChild(inputGroup);
    });
}

function validateInput(input, feature, validationMsg) {
    const value = parseFloat(input.value);
    const inputGroup = input.parentElement;
    
    // Remove previous classes
    input.classList.remove('error', 'success');
    validationMsg.classList.remove('error', 'success');
    validationMsg.style.display = 'none';
    
    if (isNaN(value) || input.value === '') {
        input.classList.add('error');
        validationMsg.textContent = 'Please enter a valid number';
        validationMsg.classList.add('error');
        validationMsg.style.display = 'block';
        return false;
    }
    
    if (value < 0) {
        input.classList.add('error');
        validationMsg.textContent = 'Value cannot be negative';
        validationMsg.classList.add('error');
        validationMsg.style.display = 'block';
        return false;
    }
    
    if (value > feature.max * 2) {
        input.classList.add('error');
        validationMsg.textContent = `Value seems too high (max: ${feature.max.toFixed(1)})`;
        validationMsg.classList.add('error');
        validationMsg.style.display = 'block';
        return false;
    }
    
    if (value < feature.min * 0.5) {
        input.classList.add('error');
        validationMsg.textContent = `Value seems too low (min: ${feature.min.toFixed(1)})`;
        validationMsg.classList.add('error');
        validationMsg.style.display = 'block';
        return false;
    }
    
    // Valid input
    input.classList.add('success');
    validationMsg.textContent = 'Looks good!';
    validationMsg.classList.add('success');
    validationMsg.style.display = 'block';
    
    // Hide success message after 2 seconds
    setTimeout(() => {
        if (validationMsg.classList.contains('success')) {
            validationMsg.style.display = 'none';
        }
    }, 2000);
    
    return true;
}

function validateForm() {
    let isValid = true;
    const inputs = document.querySelectorAll('#formGrid input');
    
    inputs.forEach(input => {
        const feature = featureInfo.find(f => 
            f.name.toLowerCase().replace(' ', '_') === input.id
        );
        
        if (feature) {
            const validationMsg = input.parentElement.querySelector('.validation-message');
            if (!validateInput(input, feature, validationMsg)) {
                isValid = false;
            }
        }
    });
    
    return isValid;
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Validate form first
    if (!validateForm()) {
        showToast('Please correct the validation errors before submitting', 'error');
        return;
    }
    
    showLoadingState();
    
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
            showToast('Error: ' + (data.error || 'Prediction failed'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    } finally {
        hideLoadingState();
    }
});

function displayResults(data) {
    const { prediction, features, timestamp, prediction_id, prediction_number } = data;
    
    if (!prediction && prediction !== 0) {
        console.error('No prediction value in response:', data);
        showToast('Error: No prediction value received', 'error');
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
    
    // Add prediction metadata
    const metadataContainer = document.createElement('div');
    metadataContainer.className = 'prediction-metadata';
    metadataContainer.innerHTML = `
        <div class="metadata-item">
            <span class="metadata-label">Prediction ID:</span>
            <span class="metadata-value">${prediction_id}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Prediction #:</span>
            <span class="metadata-value">${prediction_number}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Timestamp:</span>
            <span class="metadata-value">${new Date(timestamp).toLocaleString()}</span>
        </div>
    `;
    featuresUsed.appendChild(metadataContainer);
    
    const viewBtnContainer = document.createElement('div');
    viewBtnContainer.style.marginTop = '25px';
    viewBtnContainer.style.textAlign = 'center';
    
    const viewBtn = document.createElement('button');
    viewBtn.className = 'export-btn';
    viewBtn.innerHTML = '<span class="btn-text">📊 View All Predictions</span>';
    viewBtn.onclick = () => {
        window.open('/exports', '_blank');
    };
    
    viewBtnContainer.appendChild(viewBtn);
    featuresUsed.appendChild(viewBtnContainer);
    
    resultCard.style.display = 'block';
    showToast('Prediction completed successfully!', 'success');
    
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

function downloadPredictions() {
    window.location.href = '/download-predictions';
}

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Enhanced loading animation
function showLoadingState() {
    predictBtn.disabled = true;
    predictBtn.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <span class="loading-text">Processing...</span>
        </div>
    `;
}

function hideLoadingState() {
    predictBtn.disabled = false;
    predictBtn.innerHTML = '<span class="btn-text">Predict Sales</span><span class="btn-icon">🚀</span>';
}
