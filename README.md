# 🌾 Food Supply Chain AI Platform

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python app.py
```

### Access Dashboard
Open browser to: http://localhost:5003

## Features

✨ **AI-Powered Analytics Dashboard**
💡 **AI Insights on KPI Cards**  
🤖 **AI Recommendation Boxes**
📊 **Farm Comparison Overview**
🏭 **4 Farms (Farm A, B, C, D) with Different Performance Levels**
📋 **Detailed View Pages with Pagination**
📱 **Fully Responsive Design**
⚡ **Real-Time Chart.js Visualizations**
🔍 **Performance Scoring System**
🎯 **Crop Recommendation Engine** - AI-driven crop allocation to maximize profit
📈 **Price Prediction** - 6-month crop price forecasts using SARIMA models
🤖 **Multilingual AI Chatbot** - English, Hindi, and Kannada support with Gemini API

## Farm Data

The application uses 4 separate CSV files for 4 different farms:
- **Farm A**: Excellent performance (high yield, low spoilage, high satisfaction)
- **Farm B**: Average performance (moderate metrics)
- **Farm C**: Needs attention (low yield, high spoilage, low satisfaction)
- **Farm D**: Good performance (above average metrics)

Each farm has 125 records with comprehensive data across all supply chain stages.

## File Structure

```
AI-Food-Chain/
├── app.py                          # Flask backend with all API endpoints
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── QUICK_SETUP.md                 # Quick setup guide
├── SETUP_INSTRUCTIONS.md          # Detailed setup instructions
├── farm_a_data.csv                # Farm A data
├── farm_b_data.csv                # Farm B data
├── farm_c_data.csv                # Farm C data
├── farm_d_data.csv                # Farm D data
├── food_supply_chain_data.csv     # Combined supply chain data
├── models/
│   ├── price_predictor.py         # Price prediction model utilities
│   ├── sarima_wheat_price_model.pkl
│   ├── sarima_corn_price_model.pkl
│   ├── sarima_lettuce_price_model.pkl
│   └── sarima_tomato_price_model.pkl
├── updated_farm_data/             # Updated farm data snapshots
│   ├── updated_farm_a_data.csv
│   ├── updated_farm_b_data.csv
│   ├── updated_farm_c_data.csv
│   └── updated_farm_d_data.csv
└── templates/
    └── index.html                 # Main dashboard (single-page app)
```

## Dashboard Sections

### 🎯 Crop Recommendation (NEW!)
The intelligent crop recommendation system analyzes:
- **Predicted crop prices** from SARIMA models
- **Farm's historical performance** with each crop
- **Profitability scores** based on yield, spoilage, defects, shelf life, and pest risk
- **Cross-farm optimization** to prevent market saturation

**Features:**
- View all farms' optimal crop allocations
- See profitability scores (0-100)
- Get detailed reasoning for each recommendation
- Click to view farm-specific recommendations with profit analysis
- Understand how crop allocation prevents market overlap

**Example Allocations:**
- FarmA → Tomato (Profitability: 133.74)
- FarmB → Lettuce (Profitability: 77.71)
- FarmC → Wheat (Profitability: 45.56)
- FarmD → Corn (Profitability: 109.88)

### 📈 Price Prediction
- **6-Month Forecasts** for all 4 crops (Wheat, Corn, Lettuce, Tomato)
- **SARIMA Models** with Box-Cox transformations for accurate predictions
- **Confidence Intervals** showing upper and lower bounds
- **Interactive Charts** with Chart.js visualizations
- **Price/Quintal** predictions for market planning

### Overview Tab
- **Farm Comparison**: View all 4 farms side-by-side
- **Performance Scores**: See which farms are doing well and which need attention
- **Comparative Charts**: Yield, spoilage, defects, and performance score comparisons
- **AI Insights**: Recommendations on which farms need immediate attention

### Individual Farm Tabs (Farm A, B, C, D)
1. 📊 **Overview** - Farm-specific key metrics and performance score
2. 🌱 **Production** - Yield, pest risk, harvest and machinery uptime
3. ❄️ **Storage** - Temperature, humidity, spoilage rate, shelf life
4. ⚙️ **Processing** - Defect rates, machinery uptime, packaging speed
5. 🚚 **Transportation** - Distance, fuel usage, delivery time, delays
6. 🏪 **Retail** - Inventory, sales velocity, pricing, waste
7. 👨‍👩‍👧‍👦 **Consumption** - Household waste, recipe accuracy, satisfaction
8. ♻️ **Waste** - Segregation, upcycling, biogas output
9. 🎯 **Crop Recommendation** - Farm-specific crop recommendations

## API Endpoints

### Crop Recommendation
- GET `/api/farm/crop-recommendations-all` - Optimal allocation for all farms
- GET `/api/farm/<farm_name>/crop-recommendation` - Detailed recommendation for specific farm

### Price Prediction
- GET `/api/prediction/price/<crop_name>` - Price forecast for a crop (JSON)
- GET `/api/prediction/price` - All crop price predictions (HTML page)

### Overview
- GET `/api/overview` - Compare all farms performance

### Farm-Specific
- GET `/api/farm/<farm_name>/kpis` - Farm KPI metrics
- GET `/api/farm/<farm_name>/production` - Production data
- GET `/api/farm/<farm_name>/storage` - Storage data
- GET `/api/farm/<farm_name>/processing` - Processing data
- GET `/api/farm/<farm_name>/transportation` - Transportation data
- GET `/api/farm/<farm_name>/retail` - Retail data
- GET `/api/farm/<farm_name>/consumption` - Consumption data
- GET `/api/farm/<farm_name>/waste` - Waste data

### AI Insights
- GET `/api/ai-insights/<farm_name>/<section>` - AI-generated insights for farm and section
- POST `/api/chatbot` - Multilingual AI chatbot (supports English, Hindi, Kannada)

### Details
- GET `/details/<farm_name>/<stage>` - Detailed view pages with pagination
- GET `/details/all/<stage>` - Comparison details for all farms

## Performance Scoring

Farms are scored on a 0-100 scale based on:
- Yield (20 points)
- Spoilage rate (15 points)
- Defect rate (15 points)
- Delivery delays (10 points)
- Waste percentage (10 points)
- Customer satisfaction (15 points)
- Pest risk (10 points)
- Machinery uptime (5 points)

**Performance Levels:**
- 80-100: Excellent Performance ✅
- 65-79: Good Performance ✅
- 50-64: Average Performance ⚠️
- 0-49: Needs Attention ❌

## Crop Recommendation Algorithm

The system uses a greedy optimization algorithm:

1. **Price Prediction**: SARIMA models predict next 6 months average price
2. **Profitability Calculation**: Score = Price × Yield - (Spoilage + Defects + Waste) + Quality Factors
3. **Allocation Matrix**: Creates score matrix for all farm-crop combinations
4. **Greedy Selection**: Assigns highest-scoring farm-crop pairs while preventing overlap
5. **Market Protection**: Each crop allocated to exactly one farm to maximize price

### Default Prices (Fallback)
- Wheat: ₹2200/quintal
- Corn: ₹1800/quintal
- Lettuce: ₹1200/quintal
- Tomato: ₹1500/quintal

## Sample Data Fields

Each farm CSV contains 125 records with 39 fields covering:
- **Production**: Crop type, soil moisture, temperature, rainfall, fertilizer, yield, pest risk, harvest robot uptime
- **Storage**: Temperature, humidity, spoilage rate, grading score, shelf life, storage days
- **Processing**: Process type, packaging type, packaging speed, defect rate, machinery uptime
- **Transportation**: Transport mode, distance, fuel usage, delivery time, delays, spoilage in transit
- **Retail**: Inventory, sales velocity, pricing index, waste percentage
- **Household**: Household waste, recipe accuracy, satisfaction score
- **Waste**: Waste type, segregation accuracy, upcycling rate, biogas output

## AI Chatbot with Gemini Integration

The platform includes a multilingual AI chatbot powered by Google's Gemini API.

### Setting Up Gemini API

1. **Get API Key**: 
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key for the Gemini API

2. **Set Environment Variable**:
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Linux/Mac
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. **Or Add to .env file**:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

### Using the Chatbot

- Click the chatbot button to open the chat interface
- Select language: English, Hindi, or Kannada
- Ask questions about farms, metrics, performance, comparisons, etc.
- The chatbot uses Gemini with full context of all farm data
- Farmer-focused expertise with natural conversational tone

### Supported Languages
- 🇬🇧 **English** - Professional farming English
- 🇮🇳 **Hindi** - हिंदी (Devanagari script)
- 🇮🇳 **Kannada** - ಕನ್ನಡ (Kannada script)

### Example Questions

- "Which farm is best for tomato cultivation?"
- "Compare yields across all farms"
- "What crop should Farm A grow next season?"
- "Show me storage conditions for all farms"
- "Which farm needs the most attention?"
- "What's the expected profit for lettuce in Farm D?"

## Text-to-Speech (TTS)

The chatbot supports multilingual text-to-speech:
- **English & Hindi**: Browser native TTS (Web Speech API)
- **Kannada**: Google Translate TTS (via gTTS)
- Click speaker icon to hear chatbot responses

## Environment Variables

```bash
GEMINI_API_KEY=<your-gemini-api-key>
OLLAMA_MODEL=llama2  # Optional, for local LLM fallback
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Charts**: Chart.js (data visualization)
- **ML Models**: SARIMA (price prediction), Statsmodels
- **AI**: Google Gemini API (chatbot)
- **TTS**: Web Speech API, gTTS
- **Data**: Pandas, NumPy (data processing)

## Troubleshooting

### Models Not Loading
```bash
# Test model loading
python -c "from app import load_models, trained_models; load_models(); print(trained_models)"
```

### API Endpoints Not Responding
```bash
# Check if Flask app is running
curl http://localhost:5003/api/overview
```

### Crop Recommendations Not Showing
- Ensure `models/` directory contains all 4 `.pkl` files
- Check browser console for JavaScript errors (F12)
- Verify `/api/farm/crop-recommendations-all` returns valid JSON

### Chatbot Not Working
- Verify GEMINI_API_KEY is set: `echo $env:GEMINI_API_KEY`
- Check if API key has Gemini API enabled
- Review browser console for errors

## Performance Tips

- **Caching**: Farm data is cached in memory for efficiency
- **Pagination**: Large datasets use pagination (50 records per page)
- **Lazy Loading**: Charts and data load on-demand when tabs are selected
- **Responsive Design**: Optimized for desktop, tablet, and mobile

## Future Enhancements

- Real-time data integration with IoT sensors
- Machine learning for anomaly detection
- Advanced crop rotation recommendations
- Supply chain optimization with ML
- Multi-year trend analysis
- Weather integration for crop planning
- Market price tracking and alerts

## Enjoy! 🌾✨📊



