// Interactive Fraud Detection System - Server Version
let transactionHistory = [];
let statistics = {
    total: 0,
    fraud: 0,
    legitimate: 0
};

// API Base URL
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    // Load initial data
    await loadInitialData();
    
    // Start auto-generating sample transactions
    setInterval(generateSampleTransaction, 5000);
    
    // Initialize with some sample data
    setTimeout(async () => {
        for (let i = 0; i < 3; i++) {
            setTimeout(generateSampleTransaction, i * 1000);
        }
    }, 1000);
}

async function loadInitialData() {
    try {
        // Load existing transactions
        const transactionsResponse = await fetch(`${API_BASE}/get_transactions`);
        const transactionsData = await transactionsResponse.json();
        
        if (transactionsData.success) {
            transactionHistory = transactionsData.transactions;
            updateTransactionDisplay();
        }
        
        // Load statistics
        const statsResponse = await fetch(`${API_BASE}/get_statistics`);
        const statsData = await statsResponse.json();
        
        if (statsData.success) {
            statistics = statsData.statistics;
            updateStatisticsDisplay();
        }
        
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Analyze Transaction Function
async function analyzeTransaction() {
    const cardNumber = document.getElementById('cardNumber').value;
    const amount = parseFloat(document.getElementById('transactionAmount').value);
    const merchant = document.getElementById('merchant').value;
    const location = document.getElementById('location').value;
    const time = document.getElementById('transactionTime').value;
    const type = document.getElementById('transactionType').value;
    
    // Validation
    if (!amount || !merchant || !location || !time || !type) {
        showNotification('Please fill in all transaction details', 'warning');
        return;
    }
    
    try {
        // Show loading state
        const resultsDiv = document.getElementById('analysisResults');
        const resultsContent = document.getElementById('resultsContent');
        resultsContent.innerHTML = `
            <div class="text-center py-4">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p class="mt-2 text-gray-600">Analyzing transaction...</p>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        
        // Send to server for analysis
        const response = await fetch(`${API_BASE}/analyze_transaction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cardNumber: cardNumber,
                amount: amount,
                merchant: merchant,
                location: location,
                time: time,
                transactionType: type
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update risk visualization
            updateRiskVisualization(data.risk_analysis);
            
            // Display results
            displayAnalysisResults(data.risk_analysis, data.is_fraud, data.message);
            
            // Add to transaction history
            addToTransactionHistory(data.transaction);
            
            // Update statistics
            await updateStatistics();
            
            // Show alerts if fraud detected
            if (data.is_fraud) {
                addFraudAlert(data.transaction.amount, data.transaction.merchant, data.transaction.location);
            }
            
            showNotification('Transaction analyzed successfully', 'success');
        } else {
            showNotification(data.error || 'Analysis failed', 'error');
        }
        
    } catch (error) {
        console.error('Error analyzing transaction:', error);
        showNotification('Failed to analyze transaction', 'error');
    }
}

function updateRiskVisualization(riskAnalysis) {
    // Update risk score circle
    const riskScore = document.getElementById('riskScore');
    const riskCircle = document.getElementById('riskCircle');
    const riskLevel = document.getElementById('riskLevel');
    
    riskScore.textContent = riskAnalysis.total_risk + '%';
    
    // Update circle progress
    const circumference = 2 * Math.PI * 56;
    const offset = circumference - (riskAnalysis.total_risk / 100) * circumference;
    riskCircle.style.strokeDashoffset = offset;
    
    // Update color based on risk level
    let color, levelText;
    if (riskAnalysis.total_risk < 30) {
        color = '#10b981';
        levelText = 'Low Risk';
    } else if (riskAnalysis.total_risk < 60) {
        color = '#f59e0b';
        levelText = 'Medium Risk';
    } else {
        color = '#ef4444';
        levelText = 'High Risk';
    }
    
    riskCircle.style.stroke = color;
    riskLevel.textContent = levelText;
    riskLevel.className = `mt-4 text-lg font-semibold`;
    riskLevel.style.color = color;
    
    // Update risk factor bars
    updateRiskBar('amountRisk', riskAnalysis.amount_risk);
    updateRiskBar('locationRisk', riskAnalysis.location_risk);
    updateRiskBar('timeRisk', riskAnalysis.time_risk);
    updateRiskBar('patternRisk', riskAnalysis.pattern_risk);
}

function updateRiskBar(barId, value) {
    const bar = document.getElementById(barId);
    const percent = document.getElementById(barId + 'Percent');
    
    bar.style.width = value + '%';
    percent.textContent = value + '%';
}

function displayAnalysisResults(riskAnalysis, isFraud, message) {
    const resultsDiv = document.getElementById('analysisResults');
    const resultsContent = document.getElementById('resultsContent');
    
    const statusColor = isFraud ? 'red' : 'green';
    const statusIcon = isFraud ? 'exclamation-triangle' : 'check-circle';
    const statusText = isFraud ? 'FRAUD DETECTED' : 'TRANSACTION APPROVED';
    
    resultsContent.innerHTML = `
        <div class="grid md:grid-cols-2 gap-4">
            <div class="text-center">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-${statusColor}-100 mb-3">
                    <i class="fas fa-${statusIcon} text-${statusColor}-600 text-2xl"></i>
                </div>
                <h5 class="font-bold text-${statusColor}-800">${statusText}</h5>
            </div>
            <div class="space-y-2">
                <div class="flex justify-between">
                    <span class="text-gray-600">Total Risk Score:</span>
                    <span class="font-semibold">${riskAnalysis.total_risk}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Confidence:</span>
                    <span class="font-semibold">${(100 - Math.abs(riskAnalysis.total_risk - 50)).toFixed(1)}%</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Analysis:</span>
                    <span class="font-semibold text-sm">${message}</span>
                </div>
            </div>
        </div>
        <div class="mt-4 p-3 bg-${statusColor}-50 border border-${statusColor}-200 rounded">
            <p class="text-${statusColor}-800 text-sm">
                ${isFraud ? 
                    '⚠️ This transaction shows suspicious patterns. Immediate verification required.' : 
                    '✅ Transaction appears normal and has been approved.'
                }
            </p>
        </div>
    `;
    
    resultsDiv.classList.remove('hidden');
}

function addToTransactionHistory(transaction) {
    transactionHistory.unshift(transaction);
    
    // Keep only last 10 transactions
    if (transactionHistory.length > 10) {
        transactionHistory.pop();
    }
    
    updateTransactionDisplay();
}

function updateTransactionDisplay() {
    const container = document.getElementById('recentTransactions');
    
    if (transactionHistory.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center">No transactions yet</p>';
        return;
    }
    
    container.innerHTML = transactionHistory.map((tx, index) => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition" 
             style="animation: slideIn 0.3s ease-out ${index * 0.05}s both">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full flex items-center justify-center
                            ${tx.isFraud ? 'bg-red-100' : 'bg-green-100'}">
                    <i class="fas fa-${tx.isFraud ? 'exclamation' : 'check'} 
                       text-${tx.isFraud ? 'red' : 'green'}-600"></i>
                </div>
                <div>
                    <div class="font-semibold text-sm">${tx.merchant}</div>
                    <div class="text-xs text-gray-500">${tx.cardNumber} • ${tx.time}</div>
                </div>
            </div>
            <div class="text-right">
                <div class="font-semibold">$${tx.amount.toFixed(2)}</div>
                <div class="text-xs text-gray-500">Risk: ${tx.riskScore}%</div>
            </div>
        </div>
    `).join('');
}

async function updateStatistics() {
    try {
        const response = await fetch(`${API_BASE}/get_statistics`);
        const data = await response.json();
        
        if (data.success) {
            statistics = data.statistics;
            updateStatisticsDisplay();
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

function updateStatisticsDisplay() {
    document.getElementById('totalTransactions').textContent = statistics.total;
    document.getElementById('fraudDetected').textContent = statistics.fraud;
    document.getElementById('legitimateTransactions').textContent = statistics.legitimate;
    document.getElementById('detectionRate').textContent = statistics.detection_rate + '%';
}

async function addFraudAlert(amount, merchant, location) {
    const alertsContainer = document.getElementById('fraudAlerts');
    const timestamp = new Date().toLocaleTimeString();
    
    const alertHtml = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-3" 
             style="animation: slideIn 0.5s ease-out">
            <div class="flex items-start">
                <i class="fas fa-exclamation-triangle text-red-600 mr-3 mt-1"></i>
                <div class="flex-1">
                    <div class="font-semibold text-red-800">Fraud Alert</div>
                    <div class="text-sm text-red-700 mt-1">
                        Suspicious transaction of $${amount.toFixed(2)} at ${merchant} (${location})
                    </div>
                    <div class="text-xs text-red-600 mt-1">${timestamp}</div>
                </div>
            </div>
        </div>
    `;
    
    // Insert after the first alert (system status)
    const firstAlert = alertsContainer.firstElementChild;
    firstAlert.insertAdjacentHTML('afterend', alertHtml);
    
    // Keep only last 5 alerts
    while (alertsContainer.children.length > 6) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
}

// Auto-generate sample transactions for demonstration
async function generateSampleTransaction() {
    try {
        const response = await fetch(`${API_BASE}/generate_sample_transaction`);
        const data = await response.json();
        
        if (data.success) {
            addToTransactionHistory(data.transaction);
            await updateStatistics();
            
            if (data.transaction.isFraud) {
                addFraudAlert(data.transaction.amount, data.transaction.merchant, data.transaction.location);
            }
        }
    } catch (error) {
        console.error('Error generating sample transaction:', error);
    }
}

// Reset statistics function
async function resetStatistics() {
    try {
        const response = await fetch(`${API_BASE}/reset_statistics`);
        const data = await response.json();
        
        if (data.success) {
            transactionHistory = [];
            statistics = {
                total: 0,
                fraud: 0,
                legitimate: 0
            };
            
            updateTransactionDisplay();
            updateStatisticsDisplay();
            
            // Clear alerts except system status
            const alertsContainer = document.getElementById('fraudAlerts');
            while (alertsContainer.children.length > 1) {
                alertsContainer.removeChild(alertsContainer.lastChild);
            }
            
            showNotification('Statistics reset successfully', 'success');
        }
    } catch (error) {
        console.error('Error resetting statistics:', error);
        showNotification('Failed to reset statistics', 'error');
    }
}

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);

// Notification System
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 z-50 p-4 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300`;
    
    // Set color based on type
    const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        info: 'bg-blue-500 text-white',
        warning: 'bg-yellow-500 text-white'
    };
    
    notification.className += ' ' + colors[type];
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-3"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Initialize AOS (Animate On Scroll)
AOS.init({
    duration: 1000,
    once: true,
    offset: 100
});

// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

mobileMenuBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
    mobileMenu.classList.toggle('mobile-menu-enter');
});

// Smooth Scroll Navigation
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
        // Close mobile menu if open
        mobileMenu.classList.add('hidden');
    }
}

// Navigation Active State
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (scrollY >= (sectionTop - 200)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('text-blue-600', 'font-bold');
        if (link.getAttribute('href').slice(1) === current) {
            link.classList.add('text-blue-600', 'font-bold');
        }
    });
});

// Chart.js Configuration
Chart.defaults.font.family = 'system-ui, -apple-system, sans-serif';
Chart.defaults.color = '#4b5563';

// Transaction Distribution Chart
function initTransactionChart() {
    const ctx = document.getElementById('transactionChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Legitimate', 'Fraudulent'],
            datasets: [{
                data: [99.828, 0.172],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

// Model Performance Chart
function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Speed'],
            datasets: [{
                label: 'Random Forest',
                data: [99.8, 98.5, 96.2, 97.3, 85],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
            }, {
                label: 'Logistic Regression',
                data: [98.2, 95.1, 92.8, 93.9, 95],
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderColor: 'rgba(139, 92, 246, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(139, 92, 246, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(139, 92, 246, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Feature Importance Chart
function initFeatureChart() {
    const ctx = document.getElementById('featureChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['V14', 'V4', 'V11', 'V12', 'V10', 'V17', 'V16', 'V3'],
            datasets: [{
                label: 'Feature Importance',
                data: [0.28, 0.22, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06],
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 0.3,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Importance: ' + (context.parsed.x * 100).toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

// Detection Timeline Chart
function initTimelineChart() {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    const hours = Array.from({length: 24}, (_, i) => i + ':00');
    const legitimateData = Array.from({length: 24}, () => Math.floor(Math.random() * 500) + 1000);
    const fraudulentData = Array.from({length: 24}, () => Math.floor(Math.random() * 10) + 2);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [{
                label: 'Legitimate',
                data: legitimateData,
                borderColor: 'rgba(34, 197, 94, 1)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }, {
                label: 'Fraudulent',
                data: fraudulentData,
                borderColor: 'rgba(239, 68, 68, 1)',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Transactions'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time of Day'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Initialize all charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts with a small delay to ensure canvas elements are ready
    setTimeout(() => {
        initTransactionChart();
        initPerformanceChart();
        initFeatureChart();
        initTimelineChart();
    }, 100);
});

// Contact Form Handler
document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form values
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const organization = document.getElementById('organization').value;
    const message = document.getElementById('message').value;
    
    // Simple validation
    if (!name || !email || !message) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    // Simulate form submission
    showNotification('Thank you for your message! We will get back to you soon.', 'success');
    
    // Reset form
    this.reset();
});

// Fraud Detection Simulator
function openSimulator() {
    const modal = document.getElementById('simulatorModal');
    const content = document.getElementById('simulatorContent');
    
    // Generate simulator content
    content.innerHTML = `
        <div class="space-y-6">
            <div class="bg-blue-50 rounded-lg p-4">
                <h4 class="font-bold text-blue-800 mb-2">How it works:</h4>
                <p class="text-blue-700">Enter transaction details below to see if our model detects it as fraudulent or legitimate.</p>
            </div>
            
            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Transaction Amount ($)</label>
                    <input type="number" id="simAmount" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" placeholder="100.00" value="125.50">
                </div>
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Time of Day (Hour)</label>
                    <input type="number" id="simTime" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" placeholder="14" min="0" max="23" value="14">
                </div>
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Transaction Type</label>
                    <select id="simType" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                        <option value="online">Online Purchase</option>
                        <option value="instore">In-Store Purchase</option>
                        <option value="atm">ATM Withdrawal</option>
                        <option value="transfer">Bank Transfer</option>
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Location Risk</label>
                    <select id="simRisk" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500">
                        <option value="low">Low (Home Country)</option>
                        <option value="medium">Medium (Frequent Travel)</option>
                        <option value="high">High (Unusual Location)</option>
                    </select>
                </div>
            </div>
            
            <div class="text-center">
                <button onclick="runSimulation()" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
                    <i class="fas fa-search mr-2"></i>Analyze Transaction
                </button>
            </div>
            
            <div id="simResult" class="hidden">
                <!-- Results will be displayed here -->
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function closeSimulator() {
    const modal = document.getElementById('simulatorModal');
    modal.classList.add('hidden');
}

function runSimulation() {
    const amount = parseFloat(document.getElementById('simAmount').value);
    const time = parseInt(document.getElementById('simTime').value);
    const type = document.getElementById('simType').value;
    const risk = document.getElementById('simRisk').value;
    
    // Simulate processing
    const resultDiv = document.getElementById('simResult');
    resultDiv.innerHTML = `
        <div class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">Analyzing transaction...</p>
        </div>
    `;
    resultDiv.classList.remove('hidden');
    
    // Simulate API call delay
    setTimeout(() => {
        // Simple fraud detection logic (simulated)
        let fraudScore = 0;
        let isFraud = false;
        
        // Risk factors
        if (amount > 1000) fraudScore += 20;
        if (time < 6 || time > 22) fraudScore += 15;
        if (type === 'online') fraudScore += 10;
        if (risk === 'high') fraudScore += 30;
        if (risk === 'medium') fraudScore += 15;
        
        // Add some randomness
        fraudScore += Math.random() * 20;
        
        isFraud = fraudScore > 50;
        
        // Display results
        resultDiv.innerHTML = `
            <div class="bg-white border rounded-lg p-6">
                <div class="text-center mb-6">
                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full ${isFraud ? 'bg-red-100' : 'bg-green-100'} mb-4">
                        <i class="fas fa-${isFraud ? 'exclamation-triangle text-red-600' : 'check-circle text-green-600'} text-2xl"></i>
                    </div>
                    <h4 class="text-xl font-bold ${isFraud ? 'text-red-600' : 'text-green-600'}">
                        ${isFraud ? 'FRAUD DETECTED' : 'LEGITIMATE TRANSACTION'}
                    </h4>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <div class="flex justify-between mb-2">
                            <span class="text-gray-600">Fraud Risk Score</span>
                            <span class="font-semibold">${fraudScore.toFixed(1)}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-3">
                            <div class="h-3 rounded-full transition-all duration-500 ${fraudScore > 50 ? 'bg-red-500' : fraudScore > 30 ? 'bg-yellow-500' : 'bg-green-500'}" 
                                 style="width: ${fraudScore}%"></div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="text-gray-600">Amount:</span>
                            <span class="font-semibold ml-2">$${amount.toFixed(2)}</span>
                        </div>
                        <div>
                            <span class="text-gray-600">Time:</span>
                            <span class="font-semibold ml-2">${time}:00</span>
                        </div>
                        <div>
                            <span class="text-gray-600">Type:</span>
                            <span class="font-semibold ml-2">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                        </div>
                        <div>
                            <span class="text-gray-600">Location Risk:</span>
                            <span class="font-semibold ml-2">${risk.charAt(0).toUpperCase() + risk.slice(1)}</span>
                        </div>
                    </div>
                    
                    ${isFraud ? `
                        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                            <p class="text-red-800"><strong>Action Required:</strong> Transaction blocked. Customer verification needed.</p>
                        </div>
                    ` : `
                        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                            <p class="text-green-800"><strong>Transaction Approved:</strong> No suspicious activity detected.</p>
                        </div>
                    `}
                </div>
                
                <div class="mt-6 text-center">
                    <button onclick="runSimulation()" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition">
                        <i class="fas fa-redo mr-2"></i>Try Another Transaction
                    </button>
                </div>
            </div>
        `;
    }, 2000);
}

// Close modal when clicking outside
document.getElementById('simulatorModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeSimulator();
    }
});
