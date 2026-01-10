# Sales Prediction Using Python

## Project Overview

Sales prediction focuses on estimating future product sales based on historical data and influencing factors such as advertising spend, customer reach, and platform selection. Accurate sales forecasting helps businesses plan budgets, optimize marketing strategies, and improve decision-making.

This project uses Python to analyze sales data, identify patterns, and build a predictive model that estimates future sales values. The project demonstrates how data analysis and machine learning can be applied to real-world business problems.

## Objective

- To analyze historical sales data
- To understand how different factors influence sales
- To build a machine learning model that predicts sales accurately
- To evaluate model performance using standard metrics

## Dataset Understanding

The sales dataset includes:

- Advertising expenditure (TV, Radio, Online, etc.)
- Product or service details
- Target audience metrics
- Sales figures (target variable)

The dataset is loaded using Python libraries and explored to understand structure, missing values, and relationships between variables.

## Project Workflow

### 1. Data Loading
The dataset is imported into Python using Pandas. Initial inspection is done to check rows, columns, and data types.

### 2. Data Cleaning
- Handle missing or inconsistent values
- Remove unnecessary columns if present
- Ensure numerical features are correctly formatted

### 3. Exploratory Data Analysis
- Study the relationship between advertising spend and sales
- Identify trends and patterns using statistical analysis
- Understand which features have the most impact on sales

### 4. Feature Selection
Relevant input variables are selected based on correlation and business logic. The sales column is treated as the output variable.

### 5. Model Building
A regression-based machine learning model is used:
- Linear Regression
- Multiple Linear Regression

The dataset is split into training and testing sets to ensure reliable evaluation.

### 6. Model Training
The model is trained using the training dataset to learn relationships between inputs and sales output.

### 7. Prediction
The trained model predicts sales values on unseen test data.

### 8. Model Evaluation
Model performance is evaluated using:
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- R-squared score

These metrics help determine how accurate the predictions are.

## Installation

1. Install Python 3.8 or higher

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Navigate to the project directory:
```bash
cd sales_prediction
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and go to:
```
http://localhost:5000
http://10.123.177.240:5000
```

## Expected Outcome

- A trained machine learning model capable of predicting sales
- Clear understanding of factors affecting sales performance
- Data-driven insights to support business decision-making

## Project Use Case

This project can be applied in:
- Marketing budget planning
- Advertising strategy optimization
- Business growth forecasting
- Retail and e-commerce analytics

## Conclusion

This sales prediction project demonstrates the practical application of Python and machine learning in solving business problems. By analyzing historical data and building predictive models, businesses can anticipate future sales trends and make informed strategic decisions.
