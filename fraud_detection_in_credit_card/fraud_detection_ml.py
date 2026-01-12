"""
Credit Card Fraud Detection Using Machine Learning
===============================================

This script demonstrates the complete machine learning pipeline for credit card fraud detection.
It includes data preprocessing, handling class imbalance, model training, and evaluation.

Author: ML Developer
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek
import warnings
warnings.filterwarnings('ignore')

class CreditCardFraudDetector:
    """
    A comprehensive class for credit card fraud detection using machine learning.
    """
    
    def __init__(self):
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        
    def load_data(self, filepath):
        """
        Load the credit card dataset.
        
        Args:
            filepath (str): Path to the CSV file
        """
        print("Loading dataset...")
        try:
            self.data = pd.read_csv(filepath)
            print(f"Dataset loaded successfully! Shape: {self.data.shape}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def explore_data(self):
        """
        Perform exploratory data analysis.
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return
        
        print("\n" + "="*50)
        print("EXPLORATORY DATA ANALYSIS")
        print("="*50)
        
        # Basic info
        print("\nDataset Information:")
        print(self.data.info())
        
        # Missing values
        print("\nMissing Values:")
        print(self.data.isnull().sum())
        
        # Class distribution
        print("\nClass Distribution:")
        class_counts = self.data['Class'].value_counts()
        print(class_counts)
        
        # Calculate percentages
        fraud_percentage = (class_counts[1] / len(self.data)) * 100
        legitimate_percentage = (class_counts[0] / len(self.data)) * 100
        
        print(f"\nFraudulent transactions: {fraud_percentage:.4f}% ({class_counts[1]} cases)")
        print(f"Legitimate transactions: {legitimate_percentage:.4f}% ({class_counts[0]} cases)")
        
        # Visualizations
        self._create_visualizations()
    
    def _create_visualizations(self):
        """
        Create exploratory data visualizations.
        """
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Class distribution
        class_counts = self.data['Class'].value_counts()
        axes[0, 0].pie(class_counts, labels=['Legitimate', 'Fraud'], autopct='%1.3f%%',
                      colors=['green', 'red'], startangle=90)
        axes[0, 0].set_title('Transaction Distribution')
        
        # Amount distribution
        axes[0, 1].hist(self.data['Amount'], bins=50, alpha=0.7, color='blue')
        axes[0, 1].set_title('Transaction Amount Distribution')
        axes[0, 1].set_xlabel('Amount ($)')
        axes[0, 1].set_ylabel('Frequency')
        
        # Time distribution
        axes[1, 0].hist(self.data['Time'], bins=50, alpha=0.7, color='orange')
        axes[1, 0].set_title('Transaction Time Distribution')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].set_ylabel('Frequency')
        
        # Amount by Class
        fraud_amounts = self.data[self.data['Class'] == 1]['Amount']
        legitimate_amounts = self.data[self.data['Class'] == 0]['Amount']
        
        axes[1, 1].boxplot([legitimate_amounts, fraud_amounts], 
                          labels=['Legitimate', 'Fraud'])
        axes[1, 1].set_title('Transaction Amount by Class')
        axes[1, 1].set_ylabel('Amount ($)')
        
        plt.tight_layout()
        plt.savefig('fraud_detection_eda.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def preprocess_data(self):
        """
        Preprocess the data for modeling.
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return
        
        print("\n" + "="*50)
        print("DATA PREPROCESSING")
        print("="*50)
        
        # Separate features and target
        X = self.data.drop('Class', axis=1)
        y = self.data['Class']
        
        # Scale the features
        print("Scaling features...")
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
        
        # Split the data
        print("Splitting data into train and test sets...")
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set shape: {self.X_train.shape}")
        print(f"Test set shape: {self.X_test.shape}")
        print(f"Training set class distribution: {self.y_train.value_counts().to_dict()}")
        print(f"Test set class distribution: {self.y_test.value_counts().to_dict()}")
    
    def handle_imbalance(self, method='smote'):
        """
        Handle class imbalance using various techniques.
        
        Args:
            method (str): Method to handle imbalance ('smote', 'undersample', 'smote_tomek')
        """
        if self.X_train is None:
            print("Data not preprocessed. Please preprocess data first.")
            return
        
        print(f"\n" + "="*50)
        print(f"HANDLING CLASS IMBALANCE - {method.upper()}")
        print("="*50)
        
        print(f"Original training set shape: {self.X_train.shape}")
        print(f"Original class distribution: {self.y_train.value_counts().to_dict()}")
        
        if method == 'smote':
            sampler = SMOTE(random_state=42)
        elif method == 'undersample':
            sampler = RandomUnderSampler(random_state=42)
        elif method == 'smote_tomek':
            sampler = SMOTETomek(random_state=42)
        else:
            print("Invalid method. Using SMOTE.")
            sampler = SMOTE(random_state=42)
        
        # Apply sampling
        self.X_train_resampled, self.y_train_resampled = sampler.fit_resample(
            self.X_train, self.y_train
        )
        
        print(f"Resampled training set shape: {self.X_train_resampled.shape}")
        print(f"Resampled class distribution: {self.y_train_resampled.value_counts().to_dict()}")
    
    def train_models(self):
        """
        Train multiple classification models.
        """
        if not hasattr(self, 'X_train_resampled'):
            print("Data not resampled. Please handle imbalance first.")
            return
        
        print("\n" + "="*50)
        print("TRAINING MODELS")
        print("="*50)
        
        # Define models
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100, random_state=42, n_jobs=-1
            ),
            'Logistic Regression': LogisticRegression(
                random_state=42, max_iter=1000
            ),
            'Decision Tree': DecisionTreeClassifier(
                random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                random_state=42
            )
        }
        
        # Train each model
        for name, model in models.items():
            print(f"\nTraining {name}...")
            start_time = pd.Timestamp.now()
            
            model.fit(self.X_train_resampled, self.y_train_resampled)
            
            end_time = pd.Timestamp.now()
            training_time = (end_time - start_time).total_seconds()
            
            self.models[name] = {
                'model': model,
                'training_time': training_time
            }
            
            print(f"{name} trained successfully in {training_time:.2f} seconds")
    
    def evaluate_models(self):
        """
        Evaluate all trained models.
        """
        if not self.models:
            print("No models trained. Please train models first.")
            return
        
        print("\n" + "="*50)
        print("EVALUATING MODELS")
        print("="*50)
        
        for name, model_info in self.models.items():
            print(f"\n{'='*20} {name} {'='*20}")
            
            model = model_info['model']
            
            # Make predictions
            y_pred = model.predict(self.X_test)
            y_pred_proba = model.predict_proba(self.X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred)
            recall = recall_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred)
            
            # Store results
            self.results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'training_time': model_info['training_time']
            }
            
            # Print metrics
            print(f"Accuracy: {accuracy:.4f}")
            print(f"Precision: {precision:.4f}")
            print(f"Recall: {recall:.4f}")
            print(f"F1-Score: {f1:.4f}")
            print(f"Training Time: {model_info['training_time']:.2f} seconds")
            
            # Print classification report
            print("\nClassification Report:")
            print(classification_report(self.y_test, y_pred))
            
            # Create confusion matrix
            cm = confusion_matrix(self.y_test, y_pred)
            plt.figure(figsize=(6, 4))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=['Legitimate', 'Fraud'],
                       yticklabels=['Legitimate', 'Fraud'])
            plt.title(f'Confusion Matrix - {name}')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            plt.savefig(f'confusion_matrix_{name.lower().replace(" ", "_")}.png', 
                       dpi=300, bbox_inches='tight')
            plt.show()
    
    def compare_models(self):
        """
        Compare all models and create visualization.
        """
        if not self.results:
            print("No results available. Please evaluate models first.")
            return
        
        print("\n" + "="*50)
        print("MODEL COMPARISON")
        print("="*50)
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(self.results).T
        comparison_df = comparison_df.round(4)
        
        print("\nModel Performance Comparison:")
        print(comparison_df)
        
        # Visualize comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        colors = ['blue', 'green', 'orange', 'red']
        
        for i, (metric, color) in enumerate(zip(metrics, colors)):
            ax = axes[i//2, i%2]
            comparison_df[metric].sort_values().plot(
                kind='bar', ax=ax, color=color, alpha=0.7
            )
            ax.set_title(f'{metric.replace("_", " ").title()} Comparison')
            ax.set_ylabel('Score')
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Find best model
        best_f1_model = comparison_df['f1_score'].idxmax()
        print(f"\nBest performing model based on F1-Score: {best_f1_model}")
        print(f"F1-Score: {comparison_df.loc[best_f1_model, 'f1_score']:.4f}")
        
        return best_f1_model
    
    def feature_importance(self, model_name='Random Forest'):
        """
        Analyze feature importance for tree-based models.
        """
        if model_name not in self.models:
            print(f"Model {model_name} not found.")
            return
        
        model = self.models[model_name]['model']
        
        if not hasattr(model, 'feature_importances_'):
            print(f"Model {model_name} does not support feature importance.")
            return
        
        print(f"\n" + "="*50)
        print(f"FEATURE IMPORTANCE - {model_name}")
        print("="*50)
        
        # Get feature importance
        importances = model.feature_importances_
        feature_names = self.X_train.columns
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        # Display top 10 features
        print("Top 10 Most Important Features:")
        print(importance_df.head(10))
        
        # Visualize
        plt.figure(figsize=(12, 8))
        top_features = importance_df.head(15)
        plt.barh(range(len(top_features)), top_features['importance'])
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Importance')
        plt.title(f'Top 15 Feature Importance - {model_name}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(f'feature_importance_{model_name.lower().replace(" ", "_")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def predict_transaction(self, transaction_data, model_name='Random Forest'):
        """
        Predict if a transaction is fraudulent.
        
        Args:
            transaction_data (dict): Dictionary containing transaction features
            model_name (str): Name of the model to use for prediction
        
        Returns:
            dict: Prediction results with probability
        """
        if model_name not in self.models:
            print(f"Model {model_name} not found.")
            return None
        
        model = self.models[model_name]['model']
        
        # Convert to DataFrame
        transaction_df = pd.DataFrame([transaction_data])
        
        # Scale features
        transaction_scaled = self.scaler.transform(transaction_df)
        
        # Make prediction
        prediction = model.predict(transaction_scaled)[0]
        probability = model.predict_proba(transaction_scaled)[0]
        
        result = {
            'prediction': 'Fraud' if prediction == 1 else 'Legitimate',
            'fraud_probability': probability[1],
            'legitimate_probability': probability[0],
            'model_used': model_name
        }
        
        return result
    
    def save_results(self, filename='fraud_detection_results.txt'):
        """
        Save all results to a text file.
        """
        if not self.results:
            print("No results to save.")
            return
        
        with open(filename, 'w') as f:
            f.write("Credit Card Fraud Detection Results\n")
            f.write("="*50 + "\n\n")
            
            for model_name, metrics in self.results.items():
                f.write(f"{model_name}\n")
                f.write("-" * len(model_name) + "\n")
                f.write(f"Accuracy: {metrics['accuracy']:.4f}\n")
                f.write(f"Precision: {metrics['precision']:.4f}\n")
                f.write(f"Recall: {metrics['recall']:.4f}\n")
                f.write(f"F1-Score: {metrics['f1_score']:.4f}\n")
                f.write(f"Training Time: {metrics['training_time']:.2f} seconds\n\n")
        
        print(f"Results saved to {filename}")


def main():
    """
    Main function to run the complete fraud detection pipeline.
    """
    print("Credit Card Fraud Detection Using Machine Learning")
    print("="*60)
    
    # Initialize detector
    detector = CreditCardFraudDetector()
    
    # Note: In a real scenario, you would load the actual dataset
    # For demonstration, we'll create a synthetic dataset
    print("\nNote: This is a demonstration script.")
    print("In practice, you would load the actual creditcard.csv file.")
    print("Creating synthetic dataset for demonstration...")
    
    # Create synthetic data (in real use, load from CSV)
    from sklearn.datasets import make_classification
    X, y = make_classification(
        n_samples=10000, n_features=30, n_informative=15,
        n_redundant=5, n_clusters_per_class=1, weights=[0.998, 0.002],
        flip_y=0, random_state=42
    )
    
    # Convert to DataFrame
    feature_names = [f'V{i}' for i in range(1, 30)] + ['Amount', 'Time']
    detector.data = pd.DataFrame(X, columns=feature_names)
    detector.data['Class'] = y
    
    # Run the complete pipeline
    detector.explore_data()
    detector.preprocess_data()
    detector.handle_imbalance(method='smote')
    detector.train_models()
    detector.evaluate_models()
    best_model = detector.compare_models()
    detector.feature_importance(best_model)
    detector.save_results()
    
    print("\n" + "="*60)
    print("Fraud Detection Pipeline Completed Successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
