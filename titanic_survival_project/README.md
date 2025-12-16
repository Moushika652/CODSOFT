# Titanic Survival Prediction — Project

This project builds a supervised machine-learning pipeline to predict survival on the Titanic dataset.

Structure
- src/: Python modules and scripts
- models/: saved pipeline models (created after training)
- requirements.txt: Python dependencies

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r titanic_survival_project/requirements.txt
```

2. Run training & evaluation (dataset is expected at repository root named titanic_cleaned_same_shape.csv):

```bash
python titanic_survival_project/src/train_and_evaluate.py
```

Files of interest

- [titanic_survival_project/src/data_processing.py](titanic_survival_project/src/data_processing.py)
- [titanic_survival_project/src/pipeline.py](titanic_survival_project/src/pipeline.py)
- [titanic_survival_project/src/train_and_evaluate.py](titanic_survival_project/src/train_and_evaluate.py)

Next steps
- Optionally split into train/test sets, tune hyperparameters, or add stacking ensembles.

Dataset
- This project uses the Titanic passenger dataset (892 rows). It contains features such as `Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, `Fare`, `Cabin`, `Embarked` and the binary target `Survived` (1 = survived, 0 = did not). The dataset is the public "Titanic - Machine Learning from Disaster" dataset (Kaggle). The app displays model predictions for demonstration and evaluation.
