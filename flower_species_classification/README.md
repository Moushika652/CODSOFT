# 🌸 Iris Flower Species Classification

A beautiful web application for classifying Iris flowers into three species (Setosa, Versicolor, and Virginica) using machine learning.

## 📋 Project Overview

The Iris Flower Classification project is a classic supervised machine learning classification problem. This web application allows users to input flower measurements and get instant predictions about the species of an Iris flower.

## ✨ Features

- **Modern Web Interface**: Beautiful, responsive design with smooth animations
- **Real-time Predictions**: Instant classification results with confidence scores
- **Probability Distribution**: Visual representation of prediction probabilities for all species
- **Interactive Form**: User-friendly input fields with validation
- **Machine Learning Model**: Random Forest Classifier with high accuracy (~95%+)

## 🎯 Three Iris Species

1. **Iris Setosa** 🌿 - Distinctive, easily identifiable species with smaller petals
2. **Iris Versicolor** 🌷 - Medium-sized flowers with moderate petal measurements
3. **Iris Virginica** 🌹 - Largest petals among the three Iris species

## 📊 Dataset Features

The model uses four numerical features:
- **Sepal Length** (cm)
- **Sepal Width** (cm)
- **Petal Length** (cm)
- **Petal Width** (cm)

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Processing**: NumPy, Pandas

## 📦 Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd flower_species_classification
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Enter flower measurements** in the form and click "Classify Flower" to get predictions!

## 📝 Usage

1. Enter the four measurements (Sepal Length, Sepal Width, Petal Length, Petal Width) in centimeters
2. Click the "Classify Flower" button
3. View the predicted species along with:
   - Confidence percentage
   - Probability distribution for all three species
4. Click "Classify Another Flower" to make more predictions

## 🎨 Design Features

- Gradient backgrounds with animated color shifts
- Floating petal animations
- Smooth transitions and hover effects
- Responsive design for mobile and desktop
- Modern card-based layout
- Interactive form validation

## 📈 Model Performance

The Random Forest Classifier achieves:
- **Accuracy**: ~95% or higher
- **Cross-validation**: Stable performance across different data splits
- **Training Data**: 80% of the Iris dataset (120 samples)
- **Testing Data**: 20% of the Iris dataset (30 samples)

## 🔧 Project Structure

```
flower_species_classification/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── models/               # Saved ML models (created automatically)
├── templates/            # HTML templates
│   └── index.html
└── static/               # Static files (CSS, JS)
    ├── styles.css
    └── script.js
```

## 🧪 Sample Data

Try these sample measurements:

**Iris Setosa:**
- Sepal Length: 5.1, Sepal Width: 3.5, Petal Length: 1.4, Petal Width: 0.2

**Iris Versicolor:**
- Sepal Length: 7.0, Sepal Width: 3.2, Petal Length: 4.7, Petal Width: 1.4

**Iris Virginica:**
- Sepal Length: 6.3, Sepal Width: 3.3, Petal Length: 6.0, Petal Width: 2.5

## 📚 Learning Outcomes

This project demonstrates:
- Data preprocessing and feature selection
- Supervised learning classification
- Model training and evaluation
- Web application development with Flask
- Frontend development with modern CSS/JavaScript
- API integration and real-time predictions

## 🚧 Possible Extensions

- Compare multiple ML models (KNN, SVM, Decision Trees)
- Add cross-validation visualization
- Create data visualization charts
- Add model performance metrics dashboard
- Implement model comparison features
- Add data export functionality

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

Created as part of the CODSOFT machine learning project collection.

## 🙏 Acknowledgments

- Scikit-learn for the ML framework
- Flask for the web framework
- The Iris dataset (Fisher's Iris dataset)

---

**Enjoy classifying Iris flowers! 🌸**

