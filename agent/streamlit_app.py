"""
Streamlit Business Intelligence Agent
Complete UI for autonomous business analytics
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import sys

# Import your autonomous agent
from autonomous import AutonomousBusinessAgent
from visualization_engine import VisualizationEngine

# Page config
st.set_page_config(
    page_title="AI Business Intelligence Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #000000;
    }
    .recommendation-box {
        background-color: #fff4e6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

if 'agent' not in st.session_state:
    st.session_state.agent = None

if 'viz_engine' not in st.session_state:
    st.session_state.viz_engine = None

if 'current_results' not in st.session_state:
    st.session_state.current_results = None

if 'current_chart' not in st.session_state:
    st.session_state.current_chart = None


# Helper functions
def init_agent(api_key):
    """Initialize the AI agent"""
    try:
        st.session_state.agent = AutonomousBusinessAgent(
            db_path='data/ecommerce.db',
            api_key=api_key
        )
        st.session_state.viz_engine = VisualizationEngine()
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return False


def get_database_stats():
    """Get database overview statistics"""
    try:
        conn = sqlite3.connect('data/ecommerce.db')
        
        stats = {}
        
        # Order count
        stats['orders'] = pd.read_sql("SELECT COUNT(*) as count FROM olist_orders_dataset", conn).iloc[0]['count']
        
        # Customer count
        stats['customers'] = pd.read_sql("SELECT COUNT(DISTINCT customer_unique_id) as count FROM olist_customers_dataset", conn).iloc[0]['count']
        
        # Total revenue
        revenue_query = """
        SELECT SUM(payment_value) as total 
        FROM olist_order_payments_dataset p
        JOIN olist_orders_dataset o ON p.order_id = o.order_id
        WHERE o.order_status = 'delivered'
        """
        stats['revenue'] = pd.read_sql(revenue_query, conn).iloc[0]['total']
        
        # Date range
        date_query = """
        SELECT 
            MIN(order_purchase_timestamp) as min_date,
            MAX(order_purchase_timestamp) as max_date
        FROM olist_orders_dataset
        """
        dates = pd.read_sql(date_query, conn)
        stats['date_range'] = f"{dates.iloc[0]['min_date'][:10]} to {dates.iloc[0]['max_date'][:10]}"
        
        conn.close()
        return stats
    except Exception as e:
        return None


def process_question(question):
    """Process user question and get results"""
    
    if not st.session_state.agent:
        st.error("⚠️ Please enter your API key in the sidebar first!")
        return
    
    # Add to history
    st.session_state.query_history.append({
        'question': question,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    })
    
    # Show processing
    with st.spinner('🧠 AI is thinking...'):
        try:
            # Generate SQL
            sql = st.session_state.agent._generate_sql(question)
            
            if not sql:
                st.error("❌ Couldn't generate SQL query")
                return
            
            # Execute query
            results = st.session_state.agent._run_query(sql)
            
            if results.empty:
                st.warning("📭 No results found")
                return
            
            # Analyze results
            analysis = st.session_state.agent._analyze_results(question, results)
            
            # Create visualization
            chart_path = st.session_state.viz_engine.create_visualization(
                results, question
            )
            
            # Store results
            st.session_state.current_results = {
                'question': question,
                'sql': sql,
                'data': results,
                'analysis': analysis,
                'chart': chart_path
            }
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return False


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/chatbot.png", width=80)
    st.title("🤖 AI Agent")
    st.markdown("---")
    
    # API Key input
    st.subheader("🔑 Configuration")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API key to enable the AI agent"
    )
    
    if api_key and not st.session_state.agent:
        if init_agent(api_key):
            st.success("✅ Agent initialized!")
    
    st.markdown("---")
    
    # Database Overview
    st.subheader("📊 Database Overview")
    
    stats = get_database_stats()
    
    if stats:
        st.metric("Total Orders", f"{stats['orders']:,}")
        st.metric("Unique Customers", f"{stats['customers']:,}")
        st.metric("Total Revenue", f"${stats['revenue']:,.2f}")
        st.caption(f"📅 Data: {stats['date_range']}")
    else:
        st.info("Database stats unavailable")
    
    st.markdown("---")
    
    # Quick Questions
    st.subheader("🔥 Quick Questions")
    
    quick_questions = [
        "Who are my top 10 customers?",
        "Show me monthly revenue for 2017",
        "Which product categories perform best?",
        "What's the average delivery time?",
        "Which states generate most revenue?",
        "Show me customer distribution by state"
    ]
    
    for q in quick_questions:
        if st.button(q, key=f"quick_{q}", use_container_width=True):
            if process_question(q):
                st.rerun()
    
    st.markdown("---")
    
    # Query History
    st.subheader("📜 Recent Queries")
    
    if st.session_state.query_history:
        for item in reversed(st.session_state.query_history[-5:]):
            with st.expander(f"⏱️ {item['timestamp']}"):
                st.caption(item['question'])
    else:
        st.caption("No queries yet")
    
    st.markdown("---")
    
    # Export Section
    if st.session_state.current_results:
        st.subheader("💾 Export Results")
        
        results = st.session_state.current_results
        
        # Excel export
        if st.button("📊 Download Excel", use_container_width=True):
            output_file = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            results['data'].to_excel(output_file, index=False)
            st.success(f"✅ Saved: {output_file}")
        
        # CSV export
        if st.button("📄 Download CSV", use_container_width=True):
            csv = results['data'].to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                csv,
                file_name=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


# Main content
st.markdown('<h1 class="main-header">🤖 Autonomous Business Intelligence Agent</h1>', unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #666;'>
        Ask any business question in natural language - I'll generate SQL, analyze data, and provide insights!
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Chat interface
st.subheader("💬 Ask Your Question")

col1, col2 = st.columns([4, 1])

with col1:
    user_question = st.text_input(
        "Question",
        placeholder="e.g., Who are my top customers by revenue?",
        label_visibility="collapsed"
    )

with col2:
    ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)

if ask_button and user_question:
    process_question(user_question)

st.markdown("---")

# Results Display
if st.session_state.current_results:
    results = st.session_state.current_results
    
    # Summary
    st.markdown("### 📝 Summary")
    st.markdown(f"<div class='insight-box'>{results['analysis']['summary']}</div>", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualization", "📋 Data", "💡 Insights", "🔧 Technical"])
    
    with tab1:
        st.markdown("### 📊 Visualization")
        
        if results['chart'] and os.path.exists(results['chart']):
            st.image(results['chart'], use_container_width=True)
        else:
            st.info("No visualization available for this query")
    
    with tab2:
        st.markdown("### 📋 Data Results")
        
        # Show data
        st.dataframe(
            results['data'],
            use_container_width=True,
            height=400
        )
        
        # Data stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Rows", len(results['data']))
        
        with col2:
            st.metric("Columns", len(results['data'].columns))
        
        with col3:
            numeric_cols = results['data'].select_dtypes(include=['number']).columns
            st.metric("Numeric Columns", len(numeric_cols))
    
    with tab3:
        st.markdown("### 💡 Key Insights")
        
        if results['analysis'].get('insights'):
            for i, insight in enumerate(results['analysis']['insights'], 1):
                st.markdown(f"<div class='insight-box'><strong>{i}.</strong> {insight}</div>", unsafe_allow_html=True)
        
        st.markdown("### 🎯 Recommendations")
        
        if results['analysis'].get('recommendations'):
            for i, rec in enumerate(results['analysis']['recommendations'], 1):
                st.markdown(f"<div class='recommendation-box'><strong>{i}.</strong> {rec}</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 🔧 Technical Details")
        
        st.markdown("**Generated SQL Query:**")
        st.code(results['sql'], language='sql')
        
        st.markdown("**Execution Time:** < 1 second")
        st.markdown(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    # Welcome message
    st.info("""
        👋 **Welcome!** Here's how to get started:
        
        1. Enter your Groq API key in the sidebar
        2. Type your business question above or use quick questions
        3. Get instant insights with visualizations!
        
        **Example questions:**
        - Who are my top customers?
        - Show me monthly revenue trends
        - Which products sell best?
        - What's our average delivery time by state?
    """)
    
    # Show example
    st.markdown("### 🎬 Example Output")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Question:** *Who are my top 5 customers?*")
        st.markdown("**AI generates SQL:**")
        st.code("""
SELECT 
    c.customer_unique_id,
    SUM(p.payment_value) as total_spent
FROM olist_customers_dataset c
JOIN olist_orders_dataset o 
    ON c.customer_id = o.customer_id
JOIN olist_order_payments_dataset p 
    ON o.order_id = p.order_id
GROUP BY c.customer_unique_id
ORDER BY total_spent DESC
LIMIT 5
        """, language='sql')
    
    with col2:
        st.markdown("**You receive:**")
        st.markdown("✅ Data table with results")
        st.markdown("✅ Beautiful chart visualization")
        st.markdown("✅ AI-generated insights")
        st.markdown("✅ Actionable recommendations")
        st.markdown("✅ Export options (Excel, CSV)")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        🤖 Powered by Groq AI • Built with Streamlit • Data: Brazilian E-commerce (Olist)
    </div>
""", unsafe_allow_html=True)