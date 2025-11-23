"""
Simple database test - just verify it works
"""

import sqlite3
import pandas as pd

def test_database():
    """Quick test of Brazilian dataset"""
    
    print("🔍 Testing database...\n")
    
    try:
        conn = sqlite3.connect('data/ecommerce.db')
        
        query = '''
        SELECT 
            customer_state,
            COUNT(*) as customer_count
        FROM olist_customers_dataset
        GROUP BY customer_state
        ORDER BY customer_count DESC
        LIMIT 10
        '''
        
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))
        
        conn.close()
        
        print("\n✅ Database is working!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_database()