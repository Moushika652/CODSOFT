# Movie Rating Prediction

A machine learning project that predicts movie ratings based on various features using ensemble techniques and provides a web interface for predictions.

## 🎯 Project Overview

This project implements a movie rating prediction system that analyzes movie metadata and user voting patterns to predict ratings. The system includes data preprocessing, feature engineering, model training, and a Flask-based web application for real-time predictions.

## 📁 Project Structure

```
movie_rating_prediction/
├── app.py                 # Flask web application
├── src/                   # Source code modules
│   ├── data_loading.py    # Data loading utilities
│   └── feature_engineering.py # Feature engineering functions
├── notebooks/             # Jupyter notebooks for development
│   ├── 01_eda.ipynb       # Exploratory Data Analysis
│   ├── 02_preprocessing.ipynb # Data preprocessing
│   └── 03_model_training.ipynb # Model training and evaluation
├── models/                # Trained model files
├── data/                  # Dataset files
├── templates/             # HTML templates for web app
├── results/               # Analysis results and outputs
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## 🛠️ Technologies Used

- **Backend**: Flask
- **Machine Learning**: scikit-learn
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Web Interface**: HTML templates
- **Model Interpretability**: SHAP, LIME
- **API Framework**: FastAPI (available)

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd movie_rating_prediction
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Web Application

1. Run the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the web interface to:
   - Input movie features
   - Get rating predictions
   - View model insights

### Model Training

Use the Jupyter notebooks in the `notebooks/` directory:

1. **01_eda.ipynb**: Perform exploratory data analysis
2. **02_preprocessing.ipynb**: Clean and preprocess the data
3. **03_model_training.ipynb**: Train and evaluate models

## 📊 Features

- **Data Preprocessing**: Automated data cleaning and feature engineering
- **Multiple Models**: Support for various regression algorithms
- **Feature Engineering**: Automatic creation of derived features
- **Model Persistence**: Save and load trained models
- **Web Interface**: User-friendly Flask application
- **Real-time Predictions**: Live rating predictions
- **Model Interpretability**: SHAP and LIME explanations

## 🎬 Data Features

The model uses various movie features including:
- Movie metadata (title, genre, director, etc.)
- Cast information
- Release details
- User voting patterns
- Budget and revenue information

## 🤖 Model Performance

The system employs ensemble methods and feature engineering to achieve accurate rating predictions. Model performance metrics are available in the training notebooks.

## 🔧 Configuration

- Model files are stored in the `models/` directory
- Processed data is stored in `data/processed/`
- Results and visualizations are saved in `results/`

## 📈 Development Workflow

1. **Data Analysis**: Use `01_eda.ipynb` to understand the dataset
2. **Preprocessing**: Apply cleaning and transformation in `02_preprocessing.ipynb`
3. **Model Training**: Train and evaluate models in `03_model_training.ipynb`
4. **Deployment**: Use `app.py` for the web application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔍 Future Enhancements

- Integration with real-time movie APIs
- Advanced ensemble methods
- User recommendation system
- Mobile application interface
- Deep learning models


# Conclusion
The project is the practical application of machine learning in a real-world scenario. By combining data science with web development, we've created an interactive tool that can predict movie ratings with high accuracy. The project serves as an excellent example of how to build end-to-end ML applications that are both functional and user-friendly.

