"""
Visualization Engine
Automatically creates charts based on data type
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class VisualizationEngine:
    """Automatically generates appropriate visualizations"""
    
    def __init__(self, output_dir='visualizations'):
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        
        print(f"✅ Visualization Engine ready")
        print(f"📁 Charts saved to: {output_dir}/")
    
    def create_visualization(self, df, question, query_type=None):
        """
        Automatically create appropriate visualization
        
        Returns: filepath to saved chart
        """
        
        if df.empty or len(df) == 0:
            print("⚠️  No data to visualize")
            return None
        
        # Detect chart type
        chart_type = self._detect_chart_type(df, question)
        
        print(f"📊 Creating {chart_type} chart...")
        
        # Generate chart
        filepath = None
        
        try:
            if chart_type == "bar":
                filepath = self._create_bar_chart(df, question)
            elif chart_type == "line":
                filepath = self._create_line_chart(df, question)
            elif chart_type == "pie":
                filepath = self._create_pie_chart(df, question)
            elif chart_type == "horizontal_bar":
                filepath = self._create_horizontal_bar(df, question)
            else:
                filepath = self._create_bar_chart(df, question)  # Default
            
            if filepath:
                print(f"✅ Chart saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"⚠️  Visualization failed: {e}")
            return None
    
    def _detect_chart_type(self, df, question):
        """Detect appropriate chart type based on data"""
        
        question_lower = question.lower()
        
        # Check for time-series keywords
        if any(word in question_lower for word in ['monthly', 'trend', 'over time', 'timeline', 'growth']):
            return "line"
        
        # Check for comparison keywords
        if any(word in question_lower for word in ['top', 'best', 'worst', 'ranking', 'compare']):
            return "horizontal_bar"
        
        # Check for distribution keywords
        if any(word in question_lower for word in ['distribution', 'breakdown', 'share', 'percentage']):
            return "pie"
        
        # Analyze data structure
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        # If there's a date/month column, use line chart
        for col in df.columns:
            if any(word in col.lower() for word in ['date', 'month', 'year', 'time']):
                return "line"
        
        # Default
        if len(df) <= 10:
            return "horizontal_bar"
        else:
            return "bar"
    
    def _create_bar_chart(self, df, question):
        """Create vertical bar chart"""
        
        plt.figure(figsize=(12, 6))
        
        # Get columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return None
        
        x_col = df.columns[0]  # First column as X
        y_col = numeric_cols[0]  # First numeric as Y
        
        # Limit to top 15 items for readability
        plot_df = df.head(15)
        
        # Create bar chart
        bars = plt.bar(range(len(plot_df)), plot_df[y_col], color='#3498db', alpha=0.8)
        
        # Customize
        plt.xlabel(x_col, fontsize=12, fontweight='bold')
        plt.ylabel(y_col, fontsize=12, fontweight='bold')
        plt.title(self._clean_title(question), fontsize=14, fontweight='bold', pad=20)
        
        # X-axis labels
        plt.xticks(range(len(plot_df)), plot_df[x_col], rotation=45, ha='right')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_horizontal_bar(self, df, question):
        """Create horizontal bar chart (better for rankings)"""
        
        plt.figure(figsize=(12, 8))
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return None
        
        label_col = df.columns[0]
        value_col = numeric_cols[0]
        
        # Limit to top 10
        plot_df = df.head(10).sort_values(value_col, ascending=True)
        
        # Create horizontal bars
        bars = plt.barh(range(len(plot_df)), plot_df[value_col], color='#2ecc71', alpha=0.8)
        
        # Customize
        plt.yticks(range(len(plot_df)), plot_df[label_col], fontsize=11)
        plt.xlabel(value_col, fontsize=12, fontweight='bold')
        plt.title(self._clean_title(question), fontsize=14, fontweight='bold', pad=20)
        
        # Add value labels
        for i, (idx, row) in enumerate(plot_df.iterrows()):
            value = row[value_col]
            plt.text(value, i, f'  {value:,.0f}', 
                    va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_line_chart(self, df, question):
        """Create line chart for time-series"""
        
        plt.figure(figsize=(14, 6))
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return None
        
        x_col = df.columns[0]
        y_col = numeric_cols[0]
        
        # Plot line
        plt.plot(range(len(df)), df[y_col], 
                marker='o', linewidth=2.5, markersize=8, 
                color='#e74c3c', alpha=0.8)
        
        # Fill area under line
        plt.fill_between(range(len(df)), df[y_col], alpha=0.2, color='#e74c3c')
        
        # Customize
        plt.xlabel(x_col, fontsize=12, fontweight='bold')
        plt.ylabel(y_col, fontsize=12, fontweight='bold')
        plt.title(self._clean_title(question), fontsize=14, fontweight='bold', pad=20)
        
        # X-axis labels
        plt.xticks(range(len(df)), df[x_col], rotation=45, ha='right')
        
        # Add value labels
        for i, value in enumerate(df[y_col]):
            plt.text(i, value, f'{value:,.0f}', 
                    ha='center', va='bottom', fontsize=9)
        
        # Grid
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_pie_chart(self, df, question):
        """Create pie chart for distributions"""
        
        plt.figure(figsize=(10, 8))
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return None
        
        label_col = df.columns[0]
        value_col = numeric_cols[0]
        
        # Limit to top 8 (too many slices = unreadable)
        plot_df = df.head(8)
        
        # Create pie chart
        colors = plt.cm.Set3(range(len(plot_df)))
        
        wedges, texts, autotexts = plt.pie(
            plot_df[value_col], 
            labels=plot_df[label_col],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=[0.05] * len(plot_df),  # Slight separation
            shadow=True
        )
        
        # Customize text
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        plt.title(self._clean_title(question), fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _clean_title(self, question):
        """Create clean chart title from question"""
        
        # Capitalize first letter
        title = question.strip()
        if title:
            title = title[0].upper() + title[1:]
        
        # Remove question mark if at end
        if title.endswith('?'):
            title = title[:-1]
        
        # Limit length
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title