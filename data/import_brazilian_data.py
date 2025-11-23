"""
Import Brazilian E-Commerce CSV files into SQLite database
"""

import pandas as pd
import sqlite3
import os

def import_brazilian_ecommerce():
    """Import all CSV files from Kaggle dataset"""
    
    print("📦 Importing Brazilian E-Commerce Dataset...\n")
    
    # Define CSV files and their table names
    csv_files = {
        'olist_customers_dataset.csv': 'olist_customers_dataset',
        'olist_orders_dataset.csv': 'olist_orders_dataset',
        'olist_order_items_dataset.csv': 'olist_order_items_dataset',
        'olist_products_dataset.csv': 'olist_products_dataset',
        'olist_sellers_dataset.csv': 'olist_sellers_dataset',
        'olist_order_payments_dataset.csv': 'olist_order_payments_dataset',
        'olist_order_reviews_dataset.csv': 'olist_order_reviews_dataset',
        'product_category_name_translation.csv': 'product_category_name_translation'
    }
    
    # Connect to database
    conn = sqlite3.connect('data/ecommerce.db')
    
    imported_count = 0
    
    for csv_file, table_name in csv_files.items():
        csv_path = f'data/{csv_file}'
        
        if os.path.exists(csv_path):
            print(f"📥 Importing {csv_file}...")
            
            try:
                # Read CSV
                df = pd.read_csv(csv_path)
                
                # Import to SQLite
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                
                print(f"   ✅ Imported {len(df):,} rows into {table_name}")
                imported_count += 1
                
            except Exception as e:
                print(f"   ⚠️  Error importing {csv_file}: {e}")
        else:
            print(f"   ⚠️  File not found: {csv_file}")
    
    conn.close()
    
    print(f"\n{'=' * 60}")
    print(f"✅ Import complete! {imported_count} tables imported")
    print(f"📍 Database location: data/ecommerce.db")
    print(f"{'=' * 60}")
    
    print("\n💡 Next: Run 'python agent\\inspect_database.py' to verify")

if __name__ == "__main__":
    import_brazilian_ecommerce()
