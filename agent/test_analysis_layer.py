"""
Test Analysis Layer - Step 2 of Autonomous Agent
Tests AI's ability to generate business insights from data
"""

from groq import Groq
import pandas as pd
import json
import re
import os

class AnalysisEngine:
    """Generates business insights from data using AI"""
    
    def __init__(self, api_key=None):
        # Initialize Groq
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("❌ Groq API key required!")
        
        self.client = Groq(api_key=self.api_key)
        print("✅ Analysis Engine ready")
    
    def analyze(self, question, df):
        """
        Analyze data and generate insights
        
        Returns:
        {
            "summary": "High-level summary",
            "insights": ["insight 1", "insight 2", "insight 3"],
            "recommendations": ["action 1", "action 2", "action 3"],
            "key_metrics": {"metric_name": value}
        }
        """
        
        if df.empty:
            return {
                "summary": "No data found",
                "insights": [],
                "recommendations": [],
                "key_metrics": {}
            }
        
        # Prepare data summary for AI
        data_summary = self._prepare_summary(df)
        
        # Generate insights with AI
        analysis = self._generate_insights(question, data_summary)
        
        return analysis
    
    def _prepare_summary(self, df):
        """Create a concise data summary for AI"""
        
        summary = {
            "row_count": len(df),
            "columns": list(df.columns),
            "sample_rows": df.head(5).to_dict('records')
        }
        
        # Calculate statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            summary["statistics"] = {}
            
            for col in numeric_cols:
                summary["statistics"][col] = {
                    "total": float(df[col].sum()),
                    "average": float(df[col].mean()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "median": float(df[col].median())
                }
        
        # Detect trends for time-series data
        if len(df) >= 3:
            # Check if there's a numeric column that could represent a trend
            for col in numeric_cols:
                values = df[col].values
                if len(values) >= 3:
                    # Simple trend detection
                    first_half = values[:len(values)//2].mean()
                    second_half = values[len(values)//2:].mean()
                    
                    if second_half > first_half * 1.1:
                        summary["trend"] = f"{col} is increasing"
                    elif second_half < first_half * 0.9:
                        summary["trend"] = f"{col} is decreasing"
                    else:
                        summary["trend"] = f"{col} is stable"
                    break
        
        return summary
    
    def _generate_insights(self, question, data_summary):
        """Use AI to generate business insights"""
        
        # Convert summary to readable format
        summary_text = json.dumps(data_summary, indent=2)
        
        prompt = f"""You are a business intelligence analyst. Analyze this data and provide actionable insights.

ORIGINAL QUESTION: {question}

DATA ANALYSIS:
{summary_text}

Your task: Provide a complete business analysis in JSON format.

Required structure:
{{
  "summary": "One sentence summarizing what the data shows",
  "insights": [
    "First key insight - what patterns or trends do you see?",
    "Second key insight - what stands out in the data?",
    "Third key insight - what's surprising or important?"
  ],
  "recommendations": [
    "First action recommendation - what should the business do?",
    "Second action recommendation - specific next step",
    "Third action recommendation - how to capitalize on the insights"
  ],
  "key_metrics": {{
    "metric_name": "human-readable value with context"
  }}
}}

Rules:
- Be specific and data-driven
- Focus on actionable insights
- Use actual numbers from the data
- Keep insights concise (1-2 sentences each)
- Make recommendations concrete and practical
- Return ONLY valid JSON, no other text

JSON Analysis:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
                
                # Validate structure
                required_keys = ["summary", "insights", "recommendations"]
                if all(key in analysis for key in required_keys):
                    return analysis
            
            # Fallback if JSON parsing fails
            return self._create_fallback_analysis(data_summary)
            
        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}")
            return self._create_fallback_analysis(data_summary)
    
    def _create_fallback_analysis(self, data_summary):
        """Create basic analysis if AI fails"""
        
        insights = []
        recommendations = []
        
        # Generate basic insights from statistics
        if "statistics" in data_summary:
            for col, stats in data_summary["statistics"].items():
                insights.append(f"{col}: ranges from {stats['min']:.2f} to {stats['max']:.2f}")
        
        if "trend" in data_summary:
            insights.append(data_summary["trend"])
        
        recommendations.append("Review the data patterns for optimization opportunities")
        recommendations.append("Monitor key metrics regularly")
        
        return {
            "summary": f"Analysis of {data_summary['row_count']} records",
            "insights": insights if insights else ["Data retrieved successfully"],
            "recommendations": recommendations,
            "key_metrics": {}
        }
    
    def format_analysis(self, analysis):
        """Format analysis for display"""
        
        output = []
        
        output.append("\n" + "="*70)
        output.append("🧠 AI ANALYSIS")
        output.append("="*70)
        
        # Summary
        output.append(f"\n📝 SUMMARY:")
        output.append(f"   {analysis['summary']}")
        
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
        
        # Key Metrics
        if analysis.get("key_metrics"):
            output.append(f"\n📊 KEY METRICS:")
            for metric, value in analysis["key_metrics"].items():
                output.append(f"   • {metric}: {value}")
        
        output.append("\n" + "="*70)
        
        return "\n".join(output)


# Test Suite
if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("🧪 ANALYSIS LAYER TEST SUITE")
    print("="*70)
    
    # Get API key
    api_key = input("\n🔑 Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ API key required!")
        exit()
    
    # Initialize analyzer
    analyzer = AnalysisEngine(api_key=api_key)
    
    print("\n" + "-"*70)
    print("Testing analysis on different data types...")
    print("-"*70)
    
    # Test Case 1: Customer spending data
    print("\n\n" + "#"*70)
    print("TEST 1: Top Customers Analysis")
    print("#"*70)
    
    customer_data = pd.DataFrame({
        'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
        'total_spent': [15000, 12000, 9500, 8200, 7800],
        'order_count': [45, 38, 32, 28, 25]
    })
    
    print("\n📊 Sample Data:")
    print(customer_data.to_string(index=False))
    
    print("\n🧠 Generating insights...")
    analysis = analyzer.analyze("Who are my top customers?", customer_data)
    print(analyzer.format_analysis(analysis))
    
    input("\nPress Enter for next test...")
    
    # Test Case 2: Monthly revenue trend
    print("\n\n" + "#"*70)
    print("TEST 2: Revenue Trend Analysis")
    print("#"*70)
    
    revenue_data = pd.DataFrame({
        'month': ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06'],
        'revenue': [50000, 55000, 52000, 63000, 71000, 78000]
    })
    
    print("\n📊 Sample Data:")
    print(revenue_data.to_string(index=False))
    
    print("\n🧠 Generating insights...")
    analysis = analyzer.analyze("Show me monthly revenue trend", revenue_data)
    print(analyzer.format_analysis(analysis))
    
    input("\nPress Enter for next test...")
    
    # Test Case 3: Product performance
    print("\n\n" + "#"*70)
    print("TEST 3: Product Category Analysis")
    print("#"*70)
    
    product_data = pd.DataFrame({
        'category': ['Electronics', 'Clothing', 'Home', 'Sports', 'Books'],
        'total_sales': [125000, 98000, 87000, 65000, 45000],
        'avg_price': [250, 45, 120, 85, 35]
    })
    
    print("\n📊 Sample Data:")
    print(product_data.to_string(index=False))
    
    print("\n🧠 Generating insights...")
    analysis = analyzer.analyze("Which product categories perform best?", product_data)
    print(analyzer.format_analysis(analysis))
    
    # Summary
    print("\n\n" + "="*70)
    print("✅ ANALYSIS TESTS COMPLETE!")
    print("="*70)
    print("\n💡 Next Step: Integrate this into the main agent!")
    print("="*70)