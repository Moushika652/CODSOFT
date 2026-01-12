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

// Tab Navigation
function switchTab(tabName, element) {
    console.log('Switching to tab:', tabName);
    
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    const targetTab = document.getElementById(tabName + '-tab');
    if (targetTab) {
        targetTab.classList.add('active');
        console.log('Tab activated:', tabName + '-tab');
    } else {
        console.error('Tab not found:', tabName + '-tab');
    }
    
    // Add active class to clicked nav tab
    if (element) {
        element.classList.add('active');
        console.log('Nav tab activated');
    }
}

// Quiz System
const quizQuestions = [
    {
        question: "Which Iris species has the smallest petals?",
        options: ["Iris Setosa", "Iris Versicolor", "Iris Virginica"],
        correct: 0,
        explanation: "Iris Setosa has the smallest petals, typically 1.0-1.9 cm in length and 0.1-0.6 cm in width."
    },
    {
        question: "What does 'Setosa' mean in Latin?",
        options: ["Small", "Bristly", "Beautiful", "Large"],
        correct: 1,
        explanation: "Setosa means 'bristly' in Latin, referring to the beard-like structures on the flower."
    },
    {
        question: "Which species is native to eastern North America?",
        options: ["Iris Setosa", "Iris Versicolor", "Iris Virginica"],
        correct: 1,
        explanation: "Iris Versicolor is native to eastern North America and often has purple-blue petals."
    },
    {
        question: "What is the typical petal length range for Iris Virginica?",
        options: ["1.0-1.9 cm", "3.0-5.1 cm", "4.5-6.9 cm", "2.0-3.4 cm"],
        correct: 2,
        explanation: "Iris Virginica has the largest petals, typically 4.5-6.9 cm in length."
    },
    {
        question: "Which measurement is most distinctive for Iris Setosa?",
        options: ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width"],
        correct: 3,
        explanation: "Petal width is most distinctive for Iris Setosa, being very small (0.1-0.6 cm)."
    },
    {
        question: "What does 'Virginica' refer to?",
        options: ["Virginia", "Virgin", "Green", "Large"],
        correct: 0,
        explanation: "Virginica means 'of Virginia' - these flowers are common in the eastern United States, including Virginia."
    },
    {
        question: "Which species has the widest range of sepal lengths?",
        options: ["Iris Setosa", "Iris Versicolor", "Iris Virginica"],
        correct: 2,
        explanation: "Iris Virginica has the widest sepal length range (4.9-7.9 cm)."
    },
    {
        question: "What color are Iris Versicolor flowers typically?",
        options: ["Red", "Yellow", "Purple-Blue", "White"],
        correct: 2,
        explanation: "Iris Versicolor flowers are typically purple-blue in color."
    },
    {
        question: "Which part of the flower is measured as 'petal' in Iris classification?",
        options: ["Outer petals", "Inner petals", "Stem", "Leaves"],
        correct: 1,
        explanation: "In Iris classification, 'petal' refers to the inner petals of the flower."
    },
    {
        question: "How many species are in the Iris dataset used for machine learning?",
        options: ["2", "3", "4", "5"],
        correct: 1,
        explanation: "The classic Iris dataset contains 3 species: Setosa, Versicolor, and Virginica."
    }
];

let currentQuizQuestion = 0;
let quizScore = 0;
let quizStreak = 0;

function startQuiz() {
    currentQuizQuestion = 0;
    quizScore = 0;
    quizStreak = 0;
    updateQuizStats();
    showQuizQuestion();
    
    document.getElementById('startQuizBtn').style.display = 'none';
    document.getElementById('nextBtn').style.display = 'none';
}

function showQuizQuestion() {
    const question = quizQuestions[currentQuizQuestion];
    document.getElementById('questionText').textContent = question.question;
    
    const optionsHtml = question.options.map((option, index) => `
        <div class="quiz-option" onclick="selectQuizAnswer(${index})">
            ${option}
        </div>
    `).join('');
    
    document.getElementById('quizOptions').innerHTML = optionsHtml;
    document.getElementById('quizFeedback').innerHTML = '';
    document.getElementById('nextBtn').style.display = 'none';
    
    // Update question number
    document.getElementById('questionNumber').textContent = `${currentQuizQuestion + 1}/${quizQuestions.length}`;
}

function selectQuizAnswer(selectedIndex) {
    const question = quizQuestions[currentQuizQuestion];
    const options = document.querySelectorAll('.quiz-option');
    
    // Disable all options
    options.forEach(option => {
        option.style.pointerEvents = 'none';
    });
    
    // Show correct/incorrect
    if (selectedIndex === question.correct) {
        options[selectedIndex].classList.add('correct');
        quizScore++;
        quizStreak++;
        document.getElementById('quizFeedback').innerHTML = `
            <div class="quiz-feedback correct">
                ✅ Correct! ${question.explanation}
            </div>
        `;
    } else {
        options[selectedIndex].classList.add('incorrect');
        options[question.correct].classList.add('correct');
        quizStreak = 0;
        document.getElementById('quizFeedback').innerHTML = `
            <div class="quiz-feedback incorrect">
                ❌ Incorrect. ${question.explanation}
            </div>
        `;
    }
    
    updateQuizStats();
    
    // Show next button or finish
    if (currentQuizQuestion < quizQuestions.length - 1) {
        document.getElementById('nextBtn').style.display = 'block';
    } else {
        document.getElementById('nextBtn').textContent = 'View Results';
        document.getElementById('nextBtn').style.display = 'block';
    }
}

function nextQuestion() {
    currentQuizQuestion++;
    
    if (currentQuizQuestion < quizQuestions.length) {
        showQuizQuestion();
    } else {
        showQuizResults();
    }
}

function showQuizResults() {
    const percentage = (quizScore / quizQuestions.length) * 100;
    let message = '';
    
    if (percentage >= 80) {
        message = '🌟 Excellent! You\'re an Iris expert!';
    } else if (percentage >= 60) {
        message = '👍 Good job! You know your Iris flowers!';
    } else if (percentage >= 40) {
        message = '📚 Not bad! Keep learning about Iris flowers!';
    } else {
        message = '🌱 Keep practicing! You\'ll get better!';
    }
    
    document.getElementById('quizQuestion').innerHTML = `
        <h3>Quiz Complete!</h3>
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 20px;">${percentage >= 80 ? '🏆' : percentage >= 60 ? '🥈' : '🥉'}</div>
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">${quizScore}/${quizQuestions.length}</div>
            <div style="font-size: 18px; color: #666; margin-bottom: 20px;">${percentage.toFixed(0)}%</div>
            <div style="font-size: 16px; margin-bottom: 30px;">${message}</div>
            <button class="quiz-btn" onclick="startQuiz()">Try Again</button>
        </div>
    `;
    
    document.getElementById('quizOptions').innerHTML = '';
    document.getElementById('quizFeedback').innerHTML = '';
    document.getElementById('nextBtn').style.display = 'none';
}

function updateQuizStats() {
    document.getElementById('quizScore').textContent = quizScore;
    document.getElementById('streakCount').textContent = quizStreak;
}

// Game System
const gameData = [
    // Setosa samples
    { sepal_length: 5.1, sepal_width: 3.5, petal_length: 1.4, petal_width: 0.2, species: 'setosa' },
    { sepal_length: 4.9, sepal_width: 3.0, petal_length: 1.4, petal_width: 0.2, species: 'setosa' },
    { sepal_length: 4.7, sepal_width: 3.2, petal_length: 1.3, petal_width: 0.2, species: 'setosa' },
    { sepal_length: 5.0, sepal_width: 3.6, petal_length: 1.4, petal_width: 0.2, species: 'setosa' },
    { sepal_length: 5.4, sepal_width: 3.9, petal_length: 1.7, petal_width: 0.4, species: 'setosa' },
    
    // Versicolor samples
    { sepal_length: 7.0, sepal_width: 3.2, petal_length: 4.7, petal_width: 1.4, species: 'versicolor' },
    { sepal_length: 6.4, sepal_width: 3.2, petal_length: 4.5, petal_width: 1.5, species: 'versicolor' },
    { sepal_length: 6.9, sepal_width: 3.1, petal_length: 4.9, petal_width: 1.5, species: 'versicolor' },
    { sepal_length: 5.5, sepal_width: 2.3, petal_length: 4.0, petal_width: 1.3, species: 'versicolor' },
    { sepal_length: 6.5, sepal_width: 2.8, petal_length: 4.6, petal_width: 1.5, species: 'versicolor' },
    
    // Virginica samples
    { sepal_length: 6.3, sepal_width: 3.3, petal_length: 6.0, petal_width: 2.5, species: 'virginica' },
    { sepal_length: 5.8, sepal_width: 2.7, petal_length: 5.1, petal_width: 1.9, species: 'virginica' },
    { sepal_length: 7.1, sepal_width: 3.0, petal_length: 5.9, petal_width: 2.1, species: 'virginica' },
    { sepal_length: 6.3, sepal_width: 2.9, petal_length: 5.6, petal_width: 1.8, species: 'virginica' },
    { sepal_length: 6.5, sepal_width: 3.0, petal_length: 5.8, petal_width: 2.2, species: 'virginica' }
];

let currentGameRound = 0;
let gameScore = 0;
let gameCorrectAnswers = 0;
let currentGameData = null;

function startGame() {
    currentGameRound = 0;
    gameScore = 0;
    gameCorrectAnswers = 0;
    updateGameStats();
    nextRound();
    
    document.getElementById('startGameBtn').style.display = 'none';
    document.getElementById('nextRoundBtn').style.display = 'none';
}

function nextRound() {
    if (currentGameRound >= 10) {
        showGameResults();
        return;
    }
    
    // Select random data
    currentGameData = gameData[Math.floor(Math.random() * gameData.length)];
    
    // Display measurements
    document.getElementById('gameSepalLength').textContent = currentGameData.sepal_length.toFixed(1) + ' cm';
    document.getElementById('gameSepalWidth').textContent = currentGameData.sepal_width.toFixed(1) + ' cm';
    document.getElementById('gamePetalLength').textContent = currentGameData.petal_length.toFixed(1) + ' cm';
    document.getElementById('gamePetalWidth').textContent = currentGameData.petal_width.toFixed(1) + ' cm';
    
    // Reset options
    document.querySelectorAll('.species-option').forEach(option => {
        option.classList.remove('correct', 'incorrect');
        option.style.pointerEvents = 'auto';
    });
    
    // Clear feedback
    document.getElementById('gameFeedback').innerHTML = '';
    document.getElementById('nextRoundBtn').style.display = 'none';
    
    // Update round number
    document.getElementById('gameRound').textContent = `${currentGameRound + 1}/10`;
}

function makeGuess(species) {
    if (!currentGameData) return;
    
    // Disable all options
    document.querySelectorAll('.species-option').forEach(option => {
        option.style.pointerEvents = 'none';
    });
    
    // Check answer
    const correct = species === currentGameData.species;
    
    if (correct) {
        gameScore += 10;
        gameCorrectAnswers++;
        document.querySelector(`[onclick="makeGuess('${species}')"]`).classList.add('correct');
        document.getElementById('gameFeedback').innerHTML = `
            <div class="game-feedback correct">
                ✅ Correct! This is ${species.charAt(0).toUpperCase() + species.slice(1)}!
            </div>
        `;
    } else {
        document.querySelector(`[onclick="makeGuess('${species}')"]`).classList.add('incorrect');
        document.querySelector(`[onclick="makeGuess('${currentGameData.species}')"]`).classList.add('correct');
        document.getElementById('gameFeedback').innerHTML = `
            <div class="game-feedback incorrect">
                ❌ Incorrect. This was ${currentGameData.species.charAt(0).toUpperCase() + currentGameData.species.slice(1)}.
            </div>
        `;
    }
    
    updateGameStats();
    
    // Show next button or finish
    currentGameRound++;
    if (currentGameRound < 10) {
        document.getElementById('nextRoundBtn').style.display = 'block';
    } else {
        document.getElementById('nextRoundBtn').textContent = 'View Results';
        document.getElementById('nextRoundBtn').style.display = 'block';
    }
}

function updateGameStats() {
    document.getElementById('gameScore').textContent = gameScore;
    const accuracy = currentGameRound > 0 ? (gameCorrectAnswers / currentGameRound * 100).toFixed(0) : 0;
    document.getElementById('gameAccuracy').textContent = accuracy + '%';
}

function showGameResults() {
    const accuracy = (gameCorrectAnswers / 10 * 100).toFixed(0);
    let message = '';
    let trophy = '';
    
    if (accuracy >= 80) {
        message = '🌟 Outstanding! You\'re a master at Iris identification!';
        trophy = '🏆';
    } else if (accuracy >= 60) {
        message = '👍 Great job! You have good Iris identification skills!';
        trophy = '🥈';
    } else if (accuracy >= 40) {
        message = '📚 Good effort! Keep practicing to improve!';
        trophy = '🥉';
    } else {
        message = '🌱 Keep learning! Practice makes perfect!';
        trophy = '🌱';
    }
    
    document.getElementById('gameMeasurements').innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 20px;">${trophy}</div>
            <h3>Game Complete!</h3>
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">Score: ${gameScore}/100</div>
            <div style="font-size: 18px; color: #666; margin-bottom: 10px;">Accuracy: ${accuracy}%</div>
            <div style="font-size: 16px; margin-bottom: 30px;">${message}</div>
            <button class="game-btn" onclick="startGame()">Play Again</button>
        </div>
    `;
    
    document.getElementById('gameOptions').style.display = 'none';
    document.getElementById('gameFeedback').innerHTML = '';
    document.getElementById('nextRoundBtn').style.display = 'none';
}

// Original prediction functionality
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
            showError(data.error || 'Prediction failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = originalBtnText;
    }
});

function displayResults(data) {
    const species = data.species;
    const confidence = data.confidence;
    const probabilities = data.probabilities;
    
    // Update species display
    speciesName.textContent = species;
    speciesIcon.textContent = speciesIcons[species];
    speciesDisplay.style.background = speciesColors[species];
    
    // Update confidence
    confidenceValue.textContent = confidence.toFixed(1) + '%';
    confidenceFill.style.width = confidence + '%';
    
    // Update probabilities
    probabilitiesList.innerHTML = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1])
        .map(([spec, prob]) => `
            <div class="probability-item">
                <span class="species-name">${spec}</span>
                <div class="probability-bar">
                    <div class="probability-fill" style="width: ${prob}%; background: ${speciesColors[spec]}"></div>
                </div>
                <span class="probability-value">${prob.toFixed(1)}%</span>
            </div>
        `).join('');
    
    // Show result card
    resultCard.style.display = 'block';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        background: #fee;
        color: #c00;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
        border: 1px solid #fcc;
    `;
    
    form.parentNode.insertBefore(errorDiv, form.nextSibling);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function resetForm() {
    form.reset();
    resultCard.style.display = 'none';
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌸 Iris Classification App Initialized');
    
    // Test button clicks
    document.querySelectorAll('.nav-tab').forEach(button => {
        console.log('Found nav button:', button.textContent.trim());
        button.addEventListener('click', function() {
            console.log('Button clicked:', this.textContent.trim());
        });
    });
    
    // Check if all tabs exist
    const tabs = ['predict-tab', 'learn-tab', 'quiz-tab', 'game-tab'];
    tabs.forEach(tabId => {
        const tab = document.getElementById(tabId);
        if (tab) {
            console.log(`✅ Found tab: ${tabId}`);
        } else {
            console.error(`❌ Missing tab: ${tabId}`);
        }
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Add input validation
    const inputs = form.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);
            const value = parseFloat(this.value);
            
            if (value < min) this.value = min;
            if (value > max) this.value = max;
        });
    });
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

