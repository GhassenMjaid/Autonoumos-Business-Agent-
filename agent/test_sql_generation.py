"""
Test SQL Generation - Step 1 of Autonomous Agent
Tests AI's ability to generate SQL from natural language
"""

from groq import Groq
import sqlite3
import pandas as pd
import os

class SQLGenerator:
    """Generates SQL queries from natural language using AI"""
    
    def __init__(self, db_path='data/ecommerce.db', api_key=None):
        self.db_path = db_path
        
        # Initialize Groq
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("❌ Groq API key required!")
        
        self.client = Groq(api_key=self.api_key)
        
        # Get schema once at initialization
        self.schema = self._get_schema()
        
        print(f"✅ SQL Generator ready")
        print(f"📊 Database has {len(self.schema.split('Table:')) - 1} tables")
    
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

Product Performance:
SELECT 
    prod.product_category_name,
    COUNT(DISTINCT oi.order_id) as orders,
    SUM(oi.price) as revenue
FROM olist_products_dataset prod
JOIN olist_order_items_dataset oi ON prod.product_id = oi.product_id
GROUP BY prod.product_category_name
"""
        return schema
    
    def generate_sql(self, question):
        """Generate SQL query from natural language question"""
        
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
            
            # Clean up response (remove markdown formatting)
            sql = sql.replace('```sql', '').replace('```', '').strip()
            
            # Remove any explanatory text before/after SQL
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
    
    def test_sql(self, sql):
        """Test if generated SQL is valid"""
        
        if not sql:
            return False, "No SQL provided"
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return True, df
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def test_question(self, question):
        """Full test: question -> SQL -> results"""
        
        print(f"\n{'='*70}")
        print(f"❓ Question: {question}")
        print(f"{'='*70}\n")
        
        # Generate SQL
        print("🧠 Generating SQL...")
        sql = self.generate_sql(question)
        
        if not sql:
            print("❌ Failed to generate SQL")
            return
        
        print(f"✅ Generated SQL:\n")
        print(sql)
        print()
        
        # Test SQL
        print("⚙️  Testing SQL...")
        success, result = self.test_sql(sql)
        
        if success:
            df = result
            print(f"✅ Query successful! Got {len(df)} rows\n")
            print("📊 Results:")
            print(df.head(10).to_string(index=False))
            if len(df) > 10:
                print(f"\n... and {len(df) - 10} more rows")
        else:
            print(f"❌ Query failed: {result}")
        
        print(f"\n{'='*70}\n")
        
        return success


# Test Suite
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("🧪 SQL GENERATION TEST SUITE")
    print("="*70)
    
    # Get API key
    api_key = input("\n🔑 Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ API key required!")
        exit()
    
    # Initialize generator
    generator = SQLGenerator(api_key=api_key)
    
    print("\n" + "-"*70)
    print("Testing different question types...")
    print("-"*70)
    
    # Test cases - from simple to complex
    test_questions = [
        "Who are my top 5 customers by total spending?",
        "Show me monthly revenue for 2017",
        "Which products have the highest profit margins?",
        "Which customers haven't ordered in the last 90 days?",
        "What are the top selling product categories?",
        "Show me average delivery time by state",
    ]
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n\n{'#'*70}")
        print(f"TEST {i}/{len(test_questions)}")
        print(f"{'#'*70}")
        
        success = generator.test_question(question)
        results.append(("✅" if success else "❌", question))
        
        input("\nPress Enter to continue to next test...")
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r[0] == "✅")
    
    for status, question in results:
        print(f"{status} {question}")
    
    print(f"\n{passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Ready for Step 2!")
    else:
        print("\n⚠️  Some tests failed. Let's debug before moving on.")
    
    print("="*70)