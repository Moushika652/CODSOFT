# Credit Card Fraud Detection - Server Setup

## 🚀 Quick Start

### Option 1: Easy Startup (Recommended)
```bash
python start_server.py
```
This will automatically install dependencies and start the server.

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

## 🌐 Access the Application

Once the server is running, open your browser and go to:
- **Main Application**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Check server health |
| `POST` | `/api/analyze_transaction` | Analyze a transaction for fraud |
| `GET` | `/api/get_transactions` | Get recent transaction history |
| `GET` | `/api/get_statistics` | Get current statistics |
| `GET` | `/api/generate_sample_transaction` | Generate sample transaction |
| `GET` | `/api/get_alerts` | Get recent fraud alerts |
| `GET` | `/api/reset_statistics` | Reset all data |

### API Usage Examples

#### Analyze Transaction
```bash
curl -X POST http://localhost:5000/api/analyze_transaction \
  -H "Content-Type: application/json" \
  -d '{
    "cardNumber": "1234567890123456",
    "amount": 150.00,
    "merchant": "amazon",
    "location": "online",
    "time": "14:30",
    "transactionType": "purchase"
  }'
```

#### Get Statistics
```bash
curl http://localhost:5000/api/get_statistics
```

#### Generate Sample Transaction
```bash
curl http://localhost:5000/api/generate_sample_transaction
```

## 🏗️ Project Structure

```
fraud_detection_in_credit_card/
├── server.py                 # Main Flask server
├── start_server.py          # Easy startup script
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── script.js           # Frontend JavaScript
│   └── styles.css          # Custom CSS
├── fraud_detection_ml.py   # ML implementation
└── creditcard.csv.zip      # Dataset
```

## 🔧 Configuration

### Server Settings
- **Host**: `0.0.0.0` (accessible from any network interface)
- **Port**: `5000`
- **Debug Mode**: `False` (for production)

### Environment Variables
You can create a `.env` file to configure:
```env
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
```

## 🛠️ Features

### Real-Time Fraud Detection
- **Live Transaction Analysis**: Analyze transactions in real-time
- **Risk Assessment**: Comprehensive risk scoring system
- **Alert System**: Instant fraud alerts
- **Statistics Tracking**: Live transaction statistics

### Interactive Dashboard
- **Transaction Monitor**: Real-time transaction feed
- **Risk Visualization**: Visual risk assessment
- **Historical Data**: Transaction history and patterns
- **Sample Generation**: Automatic sample transactions for demo

### Advanced Analytics
- **Multiple Risk Factors**: Amount, location, time, pattern analysis
- **Machine Learning Logic**: Sophisticated fraud detection algorithms
- **Performance Metrics**: Accuracy, precision, recall tracking

## 🔍 How It Works

### 1. Transaction Input
Users enter transaction details:
- Card number (masked)
- Transaction amount
- Merchant type
- Location (online/local/domestic/international)
- Time of transaction
- Transaction type

### 2. Risk Analysis
The system calculates risk scores for:
- **Amount Risk**: Higher amounts = higher risk
- **Location Risk**: International > Domestic > Local
- **Time Risk**: Unusual hours = higher risk
- **Pattern Risk**: Unknown merchants + transaction type

### 3. Fraud Detection
- **Total Risk Score**: Weighted combination of all factors
- **Threshold-Based**: Transactions >50% risk flagged as fraud
- **Real-Time Processing**: Instant analysis results

### 4. Alert System
- **Immediate Notifications**: Real-time fraud alerts
- **Historical Tracking**: Transaction history and patterns
- **Statistics Updates**: Live metrics and detection rates

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
Error: [Errno 48] Address already in use
```
**Solution**: Change port in `server.py` or kill existing process:
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### Dependencies Not Found
```bash
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

#### Template Not Found
```bash
jinja2.exceptions.TemplateNotFound: index.html
```
**Solution**: Ensure `templates/index.html` exists in the correct location.

#### Static Files Not Loading
**Solution**: Check that `static/` folder contains `script.js` and `styles.css`.

### Debug Mode
For development, enable debug mode in `server.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 📊 Performance

### Expected Performance
- **Response Time**: <100ms for transaction analysis
- **Concurrent Users**: 100+ simultaneous users
- **Memory Usage**: <100MB for typical usage
- **CPU Usage**: Minimal for standard operations

### Scaling
For production deployment:
- Use **Gunicorn** or **uWSGI** as WSGI server
- Add **Redis** for session management
- Implement **database** for persistent storage
- Use **load balancer** for multiple instances

## 🔒 Security Considerations

### Current Implementation
- **Input Validation**: Server-side validation for all inputs
- **CORS Enabled**: Cross-origin requests configured
- **Error Handling**: Graceful error responses
- **Data Masking**: Card numbers automatically masked

### Production Security
- **HTTPS**: Enable SSL/TLS encryption
- **Authentication**: Add user authentication system
- **Rate Limiting**: Implement API rate limiting
- **Logging**: Add comprehensive logging
- **Database Security**: Use parameterized queries

## 🚀 Deployment

### Local Development
```bash
python start_server.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "server.py"]
```

### Cloud Deployment
- **Heroku**: Easy deployment with Git
- **AWS EC2**: Full control over environment
- **Google Cloud**: Scalable cloud platform
- **Azure**: Enterprise cloud solution

## 📞 Support

### Getting Help
- **Documentation**: Check this README and inline comments
- **Issues**: Report bugs via GitHub issues
- **Community**: Join our Discord/Slack community

### Contributing
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

---

**Note**: This is a demonstration application. For production use, implement proper security measures, database integration, and comprehensive testing.
