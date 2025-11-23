"""
Test all SQL queries against database
"""

import sqlite3
import pandas as pd
import re

def extract_queries_from_file(filepath):
    """Extract individual queries from SQL file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by semicolons, but keep query text
    queries = []
    current_query = []
    
    for line in content.split('\n'):
        # Skip pure comment lines at the start
        if line.strip().startswith('--') and not current_query:
            continue
        
        current_query.append(line)
        
        # If line ends with semicolon, that's end of query
        if line.strip().endswith(';'):
            query_text = '\n'.join(current_query)
            # Only add if it has SELECT in it (actual query, not just comments)
            if 'SELECT' in query_text.upper():
                queries.append(query_text)
            current_query = []
    
    return queries

def test_queries():
    """Test each SQL file"""
    
    print("🔍 Testing All SQL Queries")
    print("=" * 80)
    
    conn = sqlite3.connect('data/ecommerce.db')
    
    sql_files = {
        'Customer Analytics': 'sql_queries/customer_analytics.sql',
        'Revenue Analytics': 'sql_queries/revenue_analytics.sql',
        'Product Analytics': 'sql_queries/product_analytics.sql',
        'Operational Analytics': 'sql_queries/operational_analytics.sql'
    }
    
    total_passed = 0
    total_failed = 0
    
    for category, sql_file in sql_files.items():
        print(f"\n📊 {category}")
        print(f"📄 File: {sql_file}")
        print("-" * 80)
        
        try:
            queries = extract_queries_from_file(sql_file)
            print(f"   Found {len(queries)} queries\n")
            
            for i, query in enumerate(queries, 1):
                # Extract query name from comments
                query_name = "Unknown"
                for line in query.split('\n'):
                    if 'Query' in line and ':' in line and '--' in line:
                        query_name = line.split(':')[1].strip()
                        break
                
                try:
                    df = pd.read_sql_query(query, conn)
                    print(f"   ✅ Query {i}: {query_name}")
                    print(f"      Results: {len(df)} rows × {len(df.columns)} columns")
                    
                    # Show sample data
                    if len(df) > 0:
                        print(f"      Sample: {list(df.columns[:3])}")
                    
                    total_passed += 1
                    
                except Exception as e:
                    print(f"   ❌ Query {i} FAILED: {query_name}")
                    print(f"      Error: {str(e)[:100]}")
                    total_failed += 1
                
                print()
        
        except FileNotFoundError:
            print(f"   ⚠️  File not found: {sql_file}\n")
        except Exception as e:
            print(f"   ❌ Error reading file: {str(e)}\n")
    
    conn.close()
    
    print("=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   Total Queries: {total_passed + total_failed}")
    print(f"   ✅ Passed: {total_passed}")
    print(f"   ❌ Failed: {total_failed}")
    print(f"   Success Rate: {100 * total_passed / (total_passed + total_failed) if (total_passed + total_failed) > 0 else 0:.1f}%")
    print("\n✅ Query testing complete!\n")

if __name__ == "__main__":
    test_queries()
    