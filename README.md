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

✨ AI-Powered Analytics Dashboard
💡 AI Insights on KPI Cards  
🤖 AI Recommendation Boxes
📊 Farm Comparison Overview
🏭 4 Farms (Farm A, B, C, D) with Different Performance Levels
📋 Detailed View Pages with Pagination
📱 Fully Responsive Design
⚡ Real-Time Chart.js Visualizations
🔍 Performance Scoring System

## Farm Data

The application uses 4 separate CSV files for 4 different farms:
- **Farm A**: Excellent performance (high yield, low spoilage, high satisfaction)
- **Farm B**: Average performance (moderate metrics)
- **Farm C**: Needs attention (low yield, high spoilage, low satisfaction)
- **Farm D**: Good performance (above average metrics)

Each farm has 125 records with comprehensive data across all supply chain stages.

## File Structure

```
food-supply-chain/
├── app.py                    # Flask backend
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── farm_a_data.csv          # Farm A data (Excellent)
├── farm_b_data.csv          # Farm B data (Average)
├── farm_c_data.csv          # Farm C data (Needs Attention)
├── farm_d_data.csv          # Farm D data (Good)
└── templates/
    └── index.html           # Main dashboard
```

## Dashboard Sections

### Overview Tab
- **Farm Comparison**: View all 4 farms side-by-side
- **Performance Scores**: See which farms are doing well and which need attention
- **Comparative Charts**: Yield, spoilage, defects, and performance score comparisons
- **AI Insights**: Recommendations on which farms need immediate attention

### Individual Farm Tabs (Farm A, B, C, D)
1. 📊 Overview - Farm-specific key metrics and performance score
2. 🌱 Production - Yield, pest risk, harvest and machinery uptime
3. ❄️ Storage - Temperature, humidity, spoilage rate, shelf life
4. ⚙️ Processing - Defect rates, machinery uptime, packaging speed
5. 🚚 Transportation - Distance, fuel usage, delivery time, delays
6. 🏪 Retail - Inventory, sales velocity, pricing, waste
7. 👨‍👩‍👧‍👦 Consumption - Household waste, recipe accuracy, satisfaction
8. ♻️ Waste - Segregation, upcycling, biogas output

## API Endpoints

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

### Details
- GET `/details/<farm_name>/<stage>` - Detailed view pages with pagination

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

## Sample Data Fields

Each farm CSV contains 125 records with 39 fields covering:
- **Production**: Crop type, soil moisture, temperature, rainfall, fertilizer, yield, pest risk, harvest robot uptime
- **Storage**: Temperature, humidity, spoilage rate, grading score, shelf life, storage days
- **Processing**: Process type, packaging type, packaging speed, defect rate, machinery uptime
- **Transportation**: Transport mode, distance, fuel usage, delivery time, delays, spoilage in transit

## AI Chatbot with Ollama Integration

The platform includes an AI chatbot that can answer questions about farms, metrics, and performance. The chatbot is integrated with Ollama for intelligent responses.

### Setting Up Ollama

1. **Install Ollama**: Download and install Ollama from [https://ollama.ai](https://ollama.ai)

2. **Start Ollama**: Make sure Ollama is running on your local machine:
   ```bash
   ollama serve
   ```

3. **Download a Model**: Install a model of your choice:
   ```bash
   ollama pull llama2
   # Or try other models like:
   # ollama pull mistral
   # ollama pull codellama
   # ollama pull phi
   ```

4. **Configure Model (Optional)**: Set the model name via environment variable:
   ```bash
   export OLLAMA_MODEL=llama2
   # Or set it in your shell profile
   ```

### Using the Chatbot

- Click the chatbot button (bottom-right corner) to open the chat interface
- Ask questions about farms, metrics, performance, comparisons, etc.
- The chatbot uses Ollama for intelligent responses with full context of all farm data
- If Ollama is not available, the chatbot falls back to pattern matching for basic responses

### Example Questions

- "Which farm has the best performance?"
- "Compare yields across all farms"
- "What's the spoilage rate for Farm A?"
- "Show me storage conditions for all farms"
- "Which farm needs the most attention?"

Additional data fields:
- **Retail**: Inventory, sales velocity, pricing index, waste percentage
- **Household**: Household waste, recipe accuracy, satisfaction score
- **Waste**: Waste type, segregation accuracy, upcycling rate, biogas output

## AI Insights

The platform provides AI-powered insights including:
- Farm performance comparisons
- Identification of farms needing attention
- Recommendations for improvement
- Alert generation for high-risk metrics
- Optimization suggestions for each stage

## Enjoy! 🌾✨📊
