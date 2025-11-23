"""
Autonomous Business Intelligence Agent
Fully autonomous: Generates SQL, executes queries, analyzes results
"""

from groq import Groq
import sqlite3
import pandas as pd
import os
import json
import re

class AutonomousBusinessAgent:
    """Fully autonomous AI-powered business analytics agent"""
    
    def __init__(self, db_path='data/ecommerce.db', api_key=None):
        self.db_path = db_path
        
        # Initialize Groq
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("❌ Groq API key required!")
        
        self.client = Groq(api_key=self.api_key)
        
        # Load schema
        self.schema = self._get_schema()
        
        print(f"✅ Autonomous Agent ready")
        print(f"🧠 Mode: FULLY AUTONOMOUS")
        print(f"📊 Can answer ANY business question")
    
    def _get_schema(self):
        """Get database schema optimized for Olist dataset"""
        
        schema = """
OLIST E-COMMERCE DATABASE SCHEMA

🔑 KEY RELATIONSHIPS (CRITICAL FOR JOINS):
- olist_orders_dataset is the MAIN/CENTRAL table
- ALL date/time queries MUST use order_purchase_timestamp from olist_orders_dataset
- Join pattern for revenue: olist_orders_dataset → olist_order_payments_dataset (via order_id)
- Join pattern for products: olist_orders_dataset → olist_order_items_dataset → olist_products_dataset

📊 TABLES:

Table: olist_orders_dataset (MAIN TABLE - HAS ALL DATES)
  - order_id (PRIMARY KEY)
  - customer_id (FK to customers)
  - order_status (delivered, shipped, etc)
  - order_purchase_timestamp (TIMESTAMP - USE THIS FOR ALL DATE QUERIES)
  - order_approved_at (TIMESTAMP)
  - order_delivered_customer_date (TIMESTAMP)
  - order_estimated_delivery_date (TIMESTAMP)

Table: olist_order_payments_dataset (NO DATE COLUMN - JOIN TO ORDERS FOR DATES)
  - order_id (FK to orders)
  - payment_sequential
  - payment_type
  - payment_installments
  - payment_value (REVENUE AMOUNT)

Table: olist_order_items_dataset
  - order_id (FK to orders)
  - order_item_id
  - product_id (FK to products)
  - seller_id (FK to sellers)
  - price
  - freight_value

Table: olist_customers_dataset
  - customer_id (PRIMARY KEY)
  - customer_unique_id
  - customer_zip_code_prefix
  - customer_city
  - customer_state

Table: olist_products_dataset
  - product_id (PRIMARY KEY)
  - product_category_name
  - product_weight_g
  - product_length_cm

Table: olist_sellers_dataset
  - seller_id (PRIMARY KEY)
  - seller_zip_code_prefix
  - seller_city
  - seller_state

Table: olist_order_reviews_dataset
  - review_id
  - order_id (FK to orders)
  - review_score (1-5)
  - review_comment_title
  - review_comment_message

Table: product_category_name_translation
  - product_category_name (Portuguese)
  - product_category_name_english

🎯 COMMON QUERY PATTERNS:

Monthly Revenue:
SELECT 
    STRFTIME('%Y-%m', o.order_purchase_timestamp) as month,
    SUM(p.payment_value) as revenue
FROM olist_orders_dataset o
JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY month

Top Customers:
SELECT 
    c.customer_unique_id,
    c.customer_city,
    SUM(p.payment_value) as total_spent
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
GROUP BY c.customer_unique_id
ORDER BY total_spent DESC
"""
        return schema
    
    def ask(self, question):
        """
        🚀 AUTONOMOUS PIPELINE
        Handles ANY business question end-to-end
        """
        
        print(f"\n{'='*70}")
        print(f"❓ Question: {question}")
        print(f"{'='*70}\n")
        
        # STEP 1: Generate SQL with AI
        print("🧠 Step 1: Understanding question & generating SQL...")
        sql = self._generate_sql(question)
        
        if not sql:
            return "❌ Couldn't generate SQL query"
        
        print(f"✅ Generated SQL")
        print(f"📝 Query:\n{sql}\n")
        
        # STEP 2: Execute Query
        print("⚙️  Step 2: Executing query...")
        try:
            results = self._run_query(sql)
            print(f"✅ Retrieved {len(results)} rows\n")
            
            if results.empty:
                return "📭 No results found"
                
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return f"❌ Query execution failed: {str(e)[:200]}"
        
        # STEP 3: AI Analysis
        print("🔍 Step 3: Analyzing results with AI...")
        analysis = self._analyze_results(question, results)
        print("✅ Analysis complete\n")
        
        # STEP 4: Format Complete Response
        return self._format_response(question, sql, results, analysis)
    
    def _generate_sql(self, question):
        """Generate SQL query from natural language"""
        
        prompt = f"""You are an expert SQL developer working with the Olist Brazilian E-Commerce dataset.
Generate a SQLite query to answer the user's question.

{self.schema}

⚠️ CRITICAL RULES:
1. Return ONLY the SQL query - no explanations, no markdown, no commentary
2. olist_order_payments_dataset has NO date column - ALWAYS JOIN to olist_orders_dataset for dates
3. For ANY revenue/payment query with dates: JOIN olist_orders_dataset to olist_order_payments_dataset
4. Use table aliases (o, p, c, oi) to keep queries clean
5. Date format: STRFTIME('%Y-%m', o.order_purchase_timestamp) for monthly aggregations
6. Filter delivered orders: WHERE o.order_status = 'delivered'
7. Add LIMIT 100 at the end
8. Use the EXACT table names shown above (olist_orders_dataset NOT orders)

USER QUESTION: {question}

Generate the SQL query:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            sql = response.choices[0].message.content.strip()
            
            # Clean up response
            sql = sql.replace('```sql', '').replace('```', '').strip()
            
            # Extract SQL if there's extra text
            lines = sql.split('\n')
            sql_lines = []
            in_query = False
            
            for line in lines:
                if 'SELECT' in line.upper() or in_query:
                    in_query = True
                    sql_lines.append(line)
                    if line.strip().endswith(';'):
                        break
            
            return '\n'.join(sql_lines).strip()
            
        except Exception as e:
            print(f"❌ SQL generation failed: {e}")
            return None
    
    def _run_query(self, sql):
        """Execute SQL query"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(sql, conn)
            return df
        finally:
            conn.close()
    
    def _analyze_results(self, question, df):
        """AI analyzes data and generates insights"""
        
        if df.empty:
            return {
                "summary": "No data found",
                "insights": [],
                "recommendations": []
            }
        
        # Prepare data summary
        data_summary = self._prepare_summary(df)
        
        # Generate insights with AI
        summary_text = json.dumps(data_summary, indent=2)
        
        prompt = f"""You are a business intelligence analyst. Analyze this data and provide actionable insights.

ORIGINAL QUESTION: {question}

DATA ANALYSIS:
{summary_text}

Provide a complete business analysis in JSON format:

{{
  "summary": "One sentence summarizing what the data shows",
  "insights": [
    "First key insight with specific numbers",
    "Second key insight about patterns or trends",
    "Third key insight about what's important"
  ],
  "recommendations": [
    "First actionable recommendation",
    "Second specific next step",
    "Third way to capitalize on insights"
  ]
}}

Rules:
- Be specific and data-driven
- Use actual numbers from the data
- Keep insights concise (1-2 sentences)
- Make recommendations concrete
- Return ONLY valid JSON

JSON Analysis:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=600
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
                if all(key in analysis for key in ["summary", "insights", "recommendations"]):
                    return analysis
            
            return self._fallback_analysis(data_summary)
            
        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}")
            return self._fallback_analysis(data_summary)
    
    def _prepare_summary(self, df):
        """Create data summary for AI"""
        
        summary = {
            "row_count": len(df),
            "columns": list(df.columns),
            "sample_rows": df.head(3).to_dict('records')
        }
        
        # Statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            summary["statistics"] = {}
            
            for col in numeric_cols:
                summary["statistics"][col] = {
                    "total": float(df[col].sum()),
                    "average": float(df[col].mean()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
        
        return summary
    
    def _fallback_analysis(self, data_summary):
        """Basic analysis if AI fails"""
        
        return {
            "summary": f"Retrieved {data_summary['row_count']} records",
            "insights": ["Data retrieved successfully"],
            "recommendations": ["Review the data for optimization opportunities"]
        }
    
    def _format_response(self, question, sql, df, analysis):
        """Format complete autonomous response"""
        
        output = []
        
        # Header
        output.append("\n" + "="*70)
        output.append("📊 AUTONOMOUS ANALYSIS COMPLETE")
        output.append("="*70)
        
        # Summary
        output.append(f"\n📝 SUMMARY:")
        output.append(f"   {analysis['summary']}")
        
        # Data Preview
        output.append(f"\n📋 DATA ({len(df)} rows):")
        output.append(df.head(10).to_string(index=False))
        if len(df) > 10:
            output.append(f"\n   ... and {len(df) - 10} more rows")
        
        # Insights
        if analysis.get("insights"):
            output.append(f"\n💡 KEY INSIGHTS:")
            for i, insight in enumerate(analysis["insights"], 1):
                output.append(f"   {i}. {insight}")
        
        # Recommendations
        if analysis.get("recommendations"):
            output.append(f"\n🎯 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                output.append(f"   {i}. {rec}")
        
        # Technical details
        output.append(f"\n🔧 TECHNICAL DETAILS:")
        output.append(f"   SQL Query Generated:")
        for line in sql.split('\n'):
            output.append(f"   {line}")
        
        output.append("\n" + "="*70)
        
        return "\n".join(output)


# Main Program
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("🤖 AUTONOMOUS BUSINESS INTELLIGENCE AGENT")
    print("="*70)
    print("\n✨ Fully Autonomous Mode")
    print("   • Generates SQL from natural language")
    print("   • Executes queries automatically")
    print("   • Analyzes results with AI")
    print("   • Provides actionable insights")
    print("\n💬 Ask ANY business question!")
    print("\nExamples:")
    print("  • Who are my top 10 customers?")
    print("  • Show me monthly revenue for 2017")
    print("  • Which product categories perform best?")
    print("  • What's our average delivery time by state?")
    print("  • Which customers haven't ordered in 90 days?")
    print("\nType 'quit' to exit")
    print("-"*70)
    
    # Get API key
    api_key = input("\n🔑 Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ API key required!")
        exit()
    
    # Initialize autonomous agent
    try:
        agent = AutonomousBusinessAgent(api_key=api_key)
        
        print("\n" + "="*70)
        print("🚀 AGENT READY - Ask anything!")
        print("="*70)
        
        # Main loop
        while True:
            question = input("\n💬 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                continue
            
            answer = agent.ask(question)
            print(answer)
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")