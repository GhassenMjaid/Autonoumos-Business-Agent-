# Autonoumos-Business-Agent-
AI-powered autonomous business analytics agent with natural language queries


# 🤖 Autonomous Business Intelligence Agent

AI-powered business analytics agent that answers natural language questions using autonomous SQL generation and intelligent analysis.

## ✨ Features

- 🧠 **Natural Language Queries** - Ask questions in plain English
- 🔄 **Autonomous SQL Generation** - AI generates SQL on-the-fly
- 📊 **Auto Visualizations** - Smart chart generation based on data type
- 💡 **AI-Powered Insights** - Automatic business analysis and recommendations
- 💾 **Export Functionality** - Download results as Excel/CSV
- 🎨 **Interactive UI** - Beautiful Streamlit interface

## 🛠️ Tech Stack

- **Python 3.8+**
- **Streamlit** - Web interface
- **Groq AI (Llama 3.3)** - Natural language processing
- **SQLite** - Database
- **Pandas** - Data manipulation
- **Matplotlib/Seaborn** - Visualizations

## 📂 Project Structure
```
business-intelligence-agent/
├── autonomous_business_agent.py    # Core AI agent
├── visualization_engine.py          # Chart generation
├── streamlit_app.py                 # Web interface
├── data/
│   └── ecommerce.db                 # Brazilian e-commerce dataset
├── sql_queries/                     # Pre-written SQL templates
└── visualizations/                  # Generated charts
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/business-intelligence-agent.git
cd business-intelligence-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get a Groq API key:
   - Sign up at https://console.groq.com
   - Generate an API key

4. Run the app:
```bash
streamlit run streamlit_app.py
```

## 💬 Example Questions

- "Who are my top 10 customers?"
- "Show me monthly revenue for 2017"
- "Which product categories perform best?"
- "What's the average delivery time by state?"
- "Which customers haven't ordered in 90 days?"

## 📊 Dataset

Uses the Brazilian E-Commerce dataset (Olist) from Kaggle:
- 100K+ orders
- 2016-2018 timeframe
- Multiple tables (orders, customers, products, payments)

## 🎯 Key Capabilities

### 1. Autonomous SQL Generation
The agent automatically generates optimized SQL queries from natural language:

Question: "Who are my top customers?"
↓
Generated SQL:
SELECT customer_id, SUM(payment_value) as total
FROM orders JOIN payments USING(order_id)
GROUP BY customer_id
ORDER BY total DESC
LIMIT 10

### 2. Intelligent Analysis
AI analyzes results and provides:
- Summary of findings
- 3 key insights
- 3 actionable recommendations

### 3. Smart Visualizations
Automatically selects appropriate chart types:
- Bar charts for rankings
- Line charts for trends
- Pie charts for distributions

## 🔐 Security Note

Never commit your API keys! They're excluded via `.gitignore`.


## 👤 Author : Ghassen Mjaid
