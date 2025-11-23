"""
Business Analytics Agent
Answers business questions using AI and SQL
"""

from groq import Groq
import sqlite3
import pandas as pd
import os

class BusinessAgent:
    """AI-powered business analytics agent"""
    
    def __init__(self, db_path='data/ecommerce.db', api_key=None):
        self.db_path = db_path
        
        # Initialize Groq
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("❌ Groq API key required!")
        
        self.client = Groq(api_key=self.api_key)
        
        # Load SQL queries
        self.queries = self._load_queries()
        
        print(f"✅ Agent ready with {len(self.queries)} queries")
    
    def _load_queries(self):
        """Load all SQL queries from files"""
        queries = {}
        
        sql_files = {
            'Top Customers': ('sql_queries/customer_analytics.sql', 1),
            'Churn Risk': ('sql_queries/customer_analytics.sql', 2),
            'Customer Geography': ('sql_queries/customer_analytics.sql', 3),
            'Monthly Revenue': ('sql_queries/revenue_analytics.sql', 1),
            'Category Revenue': ('sql_queries/revenue_analytics.sql', 2),
            'State Revenue': ('sql_queries/revenue_analytics.sql', 3),
            'Best Products': ('sql_queries/product_analytics.sql', 1),
            'Category Performance': ('sql_queries/product_analytics.sql', 2),
            'Delivery Performance': ('sql_queries/operational_analytics.sql', 1),
            'Seller Performance': ('sql_queries/operational_analytics.sql', 2),
        }
        
        for name, (filepath, query_num) in sql_files.items():
            try:
                query = self._extract_query(filepath, query_num)
                if query:
                    queries[name] = query
            except:
                pass
        
        return queries
    
    def _extract_query(self, filepath, query_number):
        """Extract specific query from SQL file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by query markers
            parts = content.split('-- Query')
            if query_number < len(parts):
                query_section = parts[query_number]
                # Extract SQL (everything after comments until next query or end)
                lines = query_section.split('\n')
                sql_lines = []
                started = False
                
                for line in lines:
                    if 'SELECT' in line.upper():
                        started = True
                    if started:
                        sql_lines.append(line)
                        if line.strip().endswith(';'):
                            break
                
                return '\n'.join(sql_lines).strip()
        except:
            return None
    
    def ask(self, question):
        """Main method: ask a business question"""
        
        print(f"\n{'='*70}")
        print(f"❓ Question: {question}")
        print(f"{'='*70}")
        
        # Select appropriate query
        print("\n🧠 Analyzing question...")
        query_name, query_sql = self._select_query(question)
        
        if not query_sql:
            return "❌ Couldn't find relevant query"
        
        print(f"📊 Using: {query_name}")
        
        # Execute query
        print("⚙️  Running query...")
        try:
            results = self._run_query(query_sql)
            
            if results.empty:
                return "📭 No results found"
            
            print(f"✅ Got {len(results)} rows\n")
            
            # Format output
            return self._format_output(query_name, results)
            
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"
    
    def _select_query(self, question):
        """Use AI to select best query"""
        
        # List available queries
        query_list = "\n".join([f"{i+1}. {name}" for i, name in enumerate(self.queries.keys())])
        
        prompt = f"""User question: "{question}"

Available queries:
{query_list}

Which query number (1-{len(self.queries)}) best answers this?
Reply with ONLY the number."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            num = int(response.choices[0].message.content.strip()) - 1
            names = list(self.queries.keys())
            
            if 0 <= num < len(names):
                name = names[num]
                return name, self.queries[name]
                
        except:
            pass
        
        # Fallback: keyword matching
        q_lower = question.lower()
        
        if 'top customer' in q_lower or 'best customer' in q_lower:
            return 'Top Customers', self.queries.get('Top Customers')
        elif 'churn' in q_lower or 'risk' in q_lower:
            return 'Churn Risk', self.queries.get('Churn Risk')
        elif 'monthly' in q_lower or 'trend' in q_lower:
            return 'Monthly Revenue', self.queries.get('Monthly Revenue')
        elif 'category' in q_lower:
            return 'Category Revenue', self.queries.get('Category Revenue')
        elif 'product' in q_lower or 'sell' in q_lower:
            return 'Best Products', self.queries.get('Best Products')
        elif 'delivery' in q_lower:
            return 'Delivery Performance', self.queries.get('Delivery Performance')
        elif 'state' in q_lower:
            return 'State Revenue', self.queries.get('State Revenue')
        
        # Default
        first = list(self.queries.items())[0]
        return first
    
    def _run_query(self, sql):
        """Execute SQL query"""
        conn = sqlite3.connect(self.db_path)
        try:
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()
    
    def _format_output(self, name, df):
        """Format results nicely"""
        output = [f"\n📊 {name.upper()}", "="*70]
        
        # Show top 10 rows
        output.append(df.head(10).to_string(index=False))
        
        if len(df) > 10:
            output.append(f"\n... and {len(df) - 10} more rows")
        
        output.append(f"\nTotal: {len(df)} rows")
        output.append("="*70)
        
        return "\n".join(output)


# Main program
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("🤖 BUSINESS ANALYTICS AGENT")
    print("="*70)
    print("\nAsk questions about your data!")
    print("\nExamples:")
    print("  • Who are my top customers?")
    print("  • Show me monthly revenue")
    print("  • Which products sell best?")
    print("\nType 'quit' to exit")
    print("-"*70)
    
    # Get API key
    api_key = input("\n🔑 Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ API key required!")
        exit()
    
    # Initialize agent
    try:
        agent = BusinessAgent(api_key=api_key)
        
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