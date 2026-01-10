// Dashboard JavaScript for Analytics
let charts = {};
let timeSeriesData = null;
let comparisonData = null;

// Initialize dashboard
window.addEventListener('load', async () => {
    await loadDashboardData();
    initializeCharts();
    setupEventListeners();
});

async function loadDashboardData() {
    try {
        // Load time series data
        const timeSeriesResponse = await fetch('/time-series-analysis');
        if (timeSeriesResponse.ok) {
            timeSeriesData = await timeSeriesResponse.json();
        } else {
            const errorData = await timeSeriesResponse.json();
            console.error('Time series data not available:', errorData.error);
            showToast(errorData.error || 'Time series data not available', 'info');
            // Still try to load basic prediction data
            await loadBasicPredictionData();
        }

        // Load comparison data
        const comparisonResponse = await fetch('/prediction-comparison');
        if (comparisonResponse.ok) {
            comparisonData = await comparisonResponse.json();
        } else {
            const errorData = await comparisonResponse.json();
            console.error('Comparison data not available:', errorData.error);
            showToast(errorData.error || 'Comparison data not available', 'info');
        }

        updateOverviewStats();
        updateComparisonContent();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error loading dashboard data', 'error');
        // Try to load basic data as fallback
        await loadBasicPredictionData();
    }
}

async function loadBasicPredictionData() {
    try {
        // Load recent predictions directly
        const response = await fetch('/exports');
        if (response.ok) {
            const html = await response.text();
            // Extract predictions count from HTML (simple approach)
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const countElement = doc.querySelector('h2');
            if (countElement) {
                const count = parseInt(countElement.textContent.match(/\d+/)?.[0] || 0);
                if (count > 0) {
                    // Create minimal data structure for display
                    timeSeriesData = {
                        statistics: {
                            total_predictions: count,
                            sales_stats: {
                                mean: 0,
                                median: 0,
                                std: 0,
                                min: 0,
                                max: 0
                            }
                        },
                        recent_predictions: [],
                        trend_analysis: { direction: 'insufficient_data' },
                        seasonal_patterns: { hourly_average: {}, daily_average: {}, monthly_average: {} },
                        forecast: []
                    };
                    showToast(`Loaded ${count} predictions. Need 5+ for full analytics.`, 'info');
                }
            }
        }
    } catch (error) {
        console.error('Error loading basic data:', error);
    }
}

function updateOverviewStats() {
    if (!timeSeriesData) {
        const statsContainer = document.getElementById('overviewStats');
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-content">
                    <h3>No Data</h3>
                    <p>Make predictions first</p>
                </div>
            </div>
        `;
        return;
    }

    const statsContainer = document.getElementById('overviewStats');
    const stats = timeSeriesData.statistics || {};
    const trend = timeSeriesData.trend_analysis || {};

    statsContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
                <h3>${stats.total_predictions || 0}</h3>
                <p>Total Predictions</p>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-content">
                <h3>₹${(stats.sales_stats?.mean || 0).toFixed(2)}</h3>
                <p>Average Sales</p>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-content">
                <h3>${(trend.direction || 'Unknown').charAt(0).toUpperCase() + (trend.direction || 'Unknown').slice(1).replace('_', ' ')}</h3>
                <p>Trend Direction</p>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-content">
                <h3>${(trend.r_squared || 0).toFixed(3)}</h3>
                <p>Trend Accuracy</p>
            </div>
        </div>
    `;
}

function updateComparisonContent() {
    const comparisonContainer = document.getElementById('comparisonContent');
    
    if (!comparisonData) {
        comparisonContainer.innerHTML = `
            <div class="comparison-summary">
                <div class="summary-item">
                    <span class="summary-label">Status:</span>
                    <span class="summary-value">No comparison data available</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Need:</span>
                    <span class="summary-value">At least 2 predictions</span>
                </div>
            </div>
            <div style="text-align: center; padding: 40px; color: #718096;">
                <p style="font-size: 1.1rem;">📊 Make more predictions to see comparison analysis</p>
                <p style="margin-top: 10px;">Comparison features include:</p>
                <ul style="text-align: left; display: inline-block; margin-top: 10px;">
                    <li>Percentage change from average</li>
                    <li>Significance highlighting</li>
                    <li>Prediction rankings</li>
                    <li>Performance insights</li>
                </ul>
            </div>
        `;
        return;
    }

    const summary = comparisonData.summary || {};
    const comparisons = comparisonData.comparison_data || [];

    let html = `
        <div class="comparison-summary">
            <div class="summary-item">
                <span class="summary-label">Average Sales:</span>
                <span class="summary-value">₹${(summary.average_sales || 0).toFixed(2)}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Significant Predictions:</span>
                <span class="summary-value">${summary.significant_predictions || 0}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Range:</span>
                <span class="summary-value">₹${(summary.lowest_prediction || 0).toFixed(2)} - ₹${(summary.highest_prediction || 0).toFixed(2)}</span>
            </div>
        </div>
        <div class="comparison-list">
    `;

    if (comparisons.length === 0) {
        html += `
            <div style="text-align: center; padding: 40px; color: #718096;">
                <p>📊 No comparison data available</p>
            </div>
        `;
    } else {
        comparisons.forEach(comp => {
            const significanceClass = comp.significance === 'significant' ? 'significant' : 
                                     comp.significance === 'moderate' ? 'moderate' : 'normal';
            const changeIcon = comp.percentage_change > 0 ? '📈' : comp.percentage_change < 0 ? '📉' : '➡️';
            
            html += `
                <div class="comparison-item ${significanceClass}">
                    <div class="comparison-header">
                        <span class="prediction-id">${comp.prediction_id || 'N/A'}</span>
                        <span class="prediction-number">#${comp.prediction_number || 0}</span>
                    </div>
                    <div class="comparison-details">
                        <div class="sales-value">₹${(comp.predicted_sales || 0).toFixed(2)}</div>
                        <div class="change-indicator">
                            ${changeIcon} ${comp.percentage_change > 0 ? '+' : ''}${(comp.percentage_change || 0).toFixed(1)}%
                        </div>
                    </div>
                    <div class="comparison-footer">
                        <span class="timestamp">${comp.timestamp ? new Date(comp.timestamp).toLocaleString() : 'N/A'}</span>
                        <span class="significance-badge ${significanceClass}">${comp.significance || 'normal'}</span>
                    </div>
                </div>
            `;
        });
    }

    html += '</div>';
    comparisonContainer.innerHTML = html;
}

function initializeCharts() {
    if (timeSeriesData) {
        initializeChannelCharts();
        initializeTimelineChart();
        initializeForecastChart();
        initializePatternCharts();
    }
}

function initializeChannelCharts() {
    if (!timeSeriesData || !timeSeriesData.recent_predictions || timeSeriesData.recent_predictions.length === 0) {
        // Show placeholder message
        const barCtx = document.getElementById('channelBarChart');
        const pieCtx = document.getElementById('channelPieChart');
        
        if (barCtx) {
            barCtx.getContext('2d').font = '16px Poppins';
            barCtx.getContext('2d').fillText('📊 Need more predictions for channel analysis', 50, 150);
        }
        
        if (pieCtx) {
            pieCtx.getContext('2d').font = '16px Poppins';
            pieCtx.getContext('2d').fillText('📊 Need more predictions for channel analysis', 50, 150);
        }
        
        showToast('Need at least 1 prediction for channel analysis', 'info');
        return;
    }

    const recentPredictions = timeSeriesData.recent_predictions;
    const channels = ['TV', 'Radio', 'Newspaper'];
    
    // Calculate channel totals
    const channelData = channels.map(channel => {
        const total = recentPredictions.reduce((sum, pred) => sum + (pred[channel] || 0), 0);
        return total;
    });

    // Only create charts if there's actual data
    if (channelData.some(val => val > 0)) {
        // Bar Chart
        const barCtx = document.getElementById('channelBarChart').getContext('2d');
        charts.channelBar = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: channels,
                datasets: [{
                    label: 'Total Advertising Spend',
                    data: channelData,
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(79, 172, 254, 0.8)'
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(79, 172, 254, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Advertising Spend by Channel'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(0);
                            }
                        }
                    }
                }
            }
        });

        // Pie Chart
        const pieCtx = document.getElementById('channelPieChart').getContext('2d');
        charts.channelPie = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: channels,
                datasets: [{
                    data: channelData,
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(79, 172, 254, 0.8)'
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(79, 172, 254, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Channel Contribution'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ₹${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } else {
        // Show no data message
        const barCtx = document.getElementById('channelBarChart');
        const pieCtx = document.getElementById('channelPieChart');
        
        if (barCtx) {
            barCtx.getContext('2d').font = '16px Poppins';
            barCtx.getContext('2d').fillText('📊 No advertising data available', 50, 150);
        }
        
        if (pieCtx) {
            pieCtx.getContext('2d').font = '16px Poppins';
            pieCtx.getContext('2d').fillText('📊 No advertising data available', 50, 150);
        }
    }
}

function initializeTimelineChart() {
    if (!timeSeriesData || !timeSeriesData.recent_predictions || timeSeriesData.recent_predictions.length === 0) {
        const ctx = document.getElementById('timelineChart');
        if (ctx) {
            ctx.getContext('2d').font = '16px Poppins';
            ctx.getContext('2d').fillText('📊 Need more predictions for timeline analysis', 50, 150);
        }
        showToast('Need at least 1 prediction for timeline analysis', 'info');
        return;
    }

    const predictions = timeSeriesData.recent_predictions;
    const labels = predictions.map(pred => new Date(pred.Timestamp).toLocaleDateString());
    const salesData = predictions.map(pred => pred.Predicted_Sales);

    const ctx = document.getElementById('timelineChart').getContext('2d');
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Sales',
                data: salesData,
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Sales Prediction Timeline'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

function initializeForecastChart() {
    if (!timeSeriesData || !timeSeriesData.forecast || timeSeriesData.forecast.length === 0) {
        const ctx = document.getElementById('forecastChart');
        if (ctx) {
            ctx.getContext('2d').font = '16px Poppins';
            ctx.getContext('2d').fillText('🔮 Need 5+ predictions for forecasting', 50, 150);
        }
        showToast('Need at least 5 predictions for forecasting', 'info');
        return;
    }

    const forecast = timeSeriesData.forecast;
    const labels = forecast.map(item => new Date(item.date).toLocaleDateString());
    const forecastData = forecast.map(item => item.predicted_sales);
    const confidenceData = forecast.map(item => item.confidence);

    const ctx = document.getElementById('forecastChart').getContext('2d');
    charts.forecast = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Forecasted Sales',
                data: forecastData,
                borderColor: 'rgba(79, 172, 254, 1)',
                backgroundColor: 'rgba(79, 172, 254, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '7-Day Sales Forecast'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

function initializePatternCharts() {
    if (!timeSeriesData || !timeSeriesData.seasonal_patterns) {
        // Show no data messages for all pattern charts
        ['hourlyChart', 'dailyChart', 'monthlyChart'].forEach(chartId => {
            const ctx = document.getElementById(chartId);
            if (ctx) {
                ctx.getContext('2d').font = '16px Poppins';
                ctx.getContext('2d').fillText('🎯 Need 5+ predictions for pattern analysis', 50, 150);
            }
        });
        showToast('Need at least 5 predictions for pattern analysis', 'info');
        return;
    }

    const patterns = timeSeriesData.seasonal_patterns;

    // Hourly Chart
    if (patterns.hourly_average && Object.keys(patterns.hourly_average).length > 0) {
        const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
        charts.hourly = new Chart(hourlyCtx, {
            type: 'line',
            data: {
                labels: Object.keys(patterns.hourly_average),
                datasets: [{
                    label: 'Average Sales by Hour',
                    data: Object.values(patterns.hourly_average),
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(0);
                            }
                        }
                    }
                }
            }
        });
    } else {
        const hourlyCtx = document.getElementById('hourlyChart');
        if (hourlyCtx) {
            hourlyCtx.getContext('2d').font = '16px Poppins';
            hourlyCtx.getContext('2d').fillText('🎯 No hourly data available', 50, 150);
        }
    }

    // Daily Chart
    if (patterns.daily_average && Object.keys(patterns.daily_average).length > 0) {
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        
        charts.daily = new Chart(dailyCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(patterns.daily_average).map(day => dayNames[day]),
                datasets: [{
                    label: 'Average Sales by Day',
                    data: Object.values(patterns.daily_average),
                    backgroundColor: 'rgba(118, 75, 162, 0.8)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(0);
                            }
                        }
                    }
                }
            }
        });
    } else {
        const dailyCtx = document.getElementById('dailyChart');
        if (dailyCtx) {
            dailyCtx.getContext('2d').font = '16px Poppins';
            dailyCtx.getContext('2d').fillText('🎯 No daily data available', 50, 150);
        }
    }

    // Monthly Chart
    if (patterns.monthly_average && Object.keys(patterns.monthly_average).length > 0) {
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        charts.monthly = new Chart(monthlyCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(patterns.monthly_average).map(month => monthNames[month - 1]),
                datasets: [{
                    label: 'Average Sales by Month',
                    data: Object.values(patterns.monthly_average),
                    backgroundColor: 'rgba(79, 172, 254, 0.8)',
                    borderColor: 'rgba(79, 172, 254, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(0);
                            }
                        }
                    }
                }
            }
        });
    } else {
        const monthlyCtx = document.getElementById('monthlyChart');
        if (monthlyCtx) {
            monthlyCtx.getContext('2d').font = '16px Poppins';
            monthlyCtx.getContext('2d').fillText('🎯 No monthly data available', 50, 150);
        }
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

function setupEventListeners() {
    // Add any additional event listeners here
}

function downloadCSV() {
    window.location.href = '/download-predictions';
}

function generatePDF() {
    window.location.href = '/generate-pdf-report';
}

// Toast notification system (reused from main script)
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
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
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
