# 💳 Credit Card Fraud Detection System

A simple and elegant web application for detecting fraudulent credit card transactions using machine learning-inspired rules and risk assessment.

## 🚀 Features

- **🎯 Simple Interface**: Clean, user-friendly design with glass morphism effects
- **💰 Indian Currency**: Supports Indian Rupee (₹) with appropriate transaction limits
- **🛡️ Real-time Detection**: Instant fraud risk analysis based on transaction parameters
- **📊 Risk Assessment**: Visual risk scoring with detailed breakdown
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **🎨 Beautiful UI**: Modern pink theme with smooth animations and transitions

## 🛠️ Technologies Used

- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+)
- **Backend**: Flask (Python)
- **Icons**: Font Awesome 6.4.0
- **Design**: Glass morphism with gradient backgrounds

## 📋 How It Works

### Risk Factors Considered

1. **Transaction Amount**
   - ₹500+: Low risk (10 points)
   - ₹2,500+: Medium risk (20 points)
   - ₹5,000+: High risk (30 points)

2. **Transaction Time**
   - 6 AM - 9 PM: Normal (0 points)
   - 9 PM - 10 PM or 6 AM - 9 AM: Medium risk (15 points)
   - 10 PM - 6 AM: High risk (25 points)

3. **Transaction Type**
   - Purchase: Low risk (10 points)
   - Withdrawal: Low risk (10 points)
   - Transfer: Medium risk (15 points)
   - Online Payment: High risk (20 points)

4. **Location**
   - Local: Low risk (10 points)
   - Domestic: Medium risk (10 points)
   - Online: High risk (20 points)
   - International: High risk (30 points)

### Risk Scoring

- **0-40%**: Low Risk (Transaction Safe ✅)
- **41-70%**: Medium Risk (Proceed with Caution ⚠️)
- **71-100%**: High Risk (Likely Fraud 🚨)

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Flask installed (`pip install flask`)

### Installation & Running

1. **Clone or download the project**
2. **Navigate to the project directory**
   ```bash
   cd fraud_detection_in_credit_card
   ```
3. **Run the simple application**
   ```bash
   python app_simple.py
   ```
4. **Open your browser**
   ```
   http://localhost:5001
   ```

## 📁 Project Structure

```
fraud_detection_in_credit_card/
├── app_simple.py              # Main Flask application
├── templates/
│   └── index_simple.html      # Frontend HTML template
├── static/
│   └── script_clean.js       # JavaScript functionality (if needed)
└── README.md                 # This file
```


### Adjusting Risk Thresholds

Modify the `calculateFraudRisk()` function in the HTML file:

```javascript
// Amount-based risk (adjusted for Indian rupee amounts)
if (amount > 5000) riskScore += 30;
else if (amount > 2500) riskScore += 20;
else if (amount > 500) riskScore += 10;
```

## 🔧 API Endpoints

- **GET /**: Main fraud detection interface
- **GET /health**: Health check endpoint

## 📱 Mobile Support

The application is fully responsive and works seamlessly on:
- 📱 Mobile phones (iOS & Android)
- 📱 Tablets (iPad & Android tablets)
- 💻 Desktop computers (Windows, Mac, Linux)

## 🛡️ Security Features

- **Client-side validation** for all input fields
- **Input sanitization** to prevent XSS attacks
- **Secure form handling** with proper error checking
- **No data storage** - All processing happens in real-time

## 🎯 Use Cases

- **Banking Applications**: Quick fraud assessment for customer transactions
- **E-commerce Platforms**: Real-time transaction validation
- **Financial Education**: Teaching about fraud detection patterns
- **Demo Purposes**: Showcasing web development and ML concepts

## 🤝 Contributing

Feel free to contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Font Awesome** for beautiful icons
- **Tailwind CSS** for responsive design
- **Flask** for the web framework
- **Glass morphism design** inspiration from modern UI trends

# Conclusion 
This project demonstrates the practical application of Python and machine learning in solving real-world financial problems. By analyzing transaction patterns and building predictive models, businesses can proactively detect fraudulent activities and protect their customers' financial data. The integration of web development technologies makes this solution accessible and user-friendly for financial institutions and businesses of all sizes.
