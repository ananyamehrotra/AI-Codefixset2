#!/usr/bin/env python3
"""
Optimized Database Insights Agent - AI CODEFIX 2025
Analyzes sales database and generates comprehensive report with visualizations.
"""

import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import datetime
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv()

# Use non-interactive backend for matplotlib
plt.switch_backend('Agg')

class DatabaseAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.output_dir = "output/reports"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def discover_tables(self):
        """Get all tables in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        # Remove duplicate tables (with and without quotes)
        unique_tables = []
        seen = set()
        for table in tables:
            clean_name = table.strip('"')
            if clean_name not in seen:
                unique_tables.append(table)
                seen.add(clean_name)
        return unique_tables
    
    def analyze_table(self, table_name, sample_size=10000):
        """Analyze a single table with optional sampling for large tables."""
        cursor = self.conn.cursor()
        
        # Get table info
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        total_rows = cursor.fetchone()[0]
        
        # Sample large tables
        if total_rows > sample_size:
            # Get sample data
            df = pd.read_sql_query(f"SELECT * FROM `{table_name}` LIMIT {sample_size}", self.conn)
            print(f"✅ Sampled {table_name}: {sample_size} of {total_rows} rows, {len(df.columns)} columns")
        else:
            df = pd.read_sql_query(f"SELECT * FROM `{table_name}`", self.conn)
            print(f"✅ Read {table_name}: {total_rows} rows, {len(df.columns)} columns")
        
        # Analyze the data
        stats = {
            'name': table_name,
            'total_rows': total_rows,
            'sampled_rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'nulls': df.isnull().sum().to_dict(),
            'duplicates': int(df.duplicated().sum()),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'text_columns': list(df.select_dtypes(include=['object']).columns),
            'data_types': df.dtypes.to_dict()
        }
        
        # Get basic statistics for numeric columns
        if stats['numeric_columns']:
            stats['numeric_stats'] = df[stats['numeric_columns']].describe().to_dict()
        
        return df, stats
    
    def generate_insights(self, all_stats):
        """Generate key business insights from the analysis."""
        insights = []
        
        # Total data overview
        total_tables = len(all_stats)
        total_records = sum(stat['total_rows'] for stat in all_stats.values())
        insights.append(f"<b>Database Overview:</b> {total_tables} tables with {total_records:,} total records")
        
        # Find largest tables
        largest_table = max(all_stats.items(), key=lambda x: x[1]['total_rows'])
        insights.append(f"<b>Largest Table:</b> {largest_table[0]} with {largest_table[1]['total_rows']:,} records")
        
        # Data quality insights
        tables_with_nulls = []
        total_nulls = 0
        for table, stats in all_stats.items():
            null_count = sum(stats['nulls'].values())
            total_nulls += null_count
            if null_count > 0:
                tables_with_nulls.append(f"{table} ({null_count} nulls)")
        
        if tables_with_nulls:
            insights.append(f"<b>Data Quality:</b> {len(tables_with_nulls)} tables have missing values (total: {total_nulls:,} nulls)")
        else:
            insights.append("<b>Data Quality:</b> Excellent - no missing values detected")
            
        return insights
    
    def create_visualizations(self, all_stats, dataframes):
        """Create professional visualizations."""
        charts = []
        
        # Chart 1: Table Size Distribution
        chart1_path = os.path.join(self.output_dir, "chart_table_distribution.png")
        self.create_table_distribution_chart(all_stats, chart1_path)
        charts.append(chart1_path)
        
        # Chart 2: Sales Analysis (from sales tables)
        chart2_path = os.path.join(self.output_dir, "chart_sales_analysis.png")
        self.create_sales_analysis_chart(dataframes, chart2_path)
        charts.append(chart2_path)
        
        # Chart 3: Data Quality Overview
        chart3_path = os.path.join(self.output_dir, "chart_data_quality.png")
        self.create_data_quality_chart(all_stats, chart3_path)
        charts.append(chart3_path)
        
        return charts
    
    def create_table_distribution_chart(self, all_stats, output_path):
        """Create a professional table size distribution chart."""
        table_names = [stats['name'] for stats in all_stats.values()]
        row_counts = [stats['total_rows'] for stats in all_stats.values()]
        
        # Create figure
        plt.figure(figsize=(14, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(table_names)))
        
        bars = plt.bar(range(len(table_names)), row_counts, color=colors, alpha=0.8, edgecolor='black')
        
        plt.title('Database Table Size Distribution', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Tables', fontsize=12)
        plt.ylabel('Number of Records', fontsize=12)
        plt.xticks(range(len(table_names)), [name.replace('dbo_', '') for name in table_names], 
                   rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, count in zip(bars, row_counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + max(row_counts)*0.01,
                    f'{count:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  📊 Created chart: {output_path}")
    
    def create_sales_analysis_chart(self, dataframes, output_path):
        """Create sales analysis visualization."""
        plt.figure(figsize=(15, 10))
        
        # Try to find sales transaction data
        sales_df = None
        for table_name, df in dataframes.items():
            if 'transaction' in table_name.lower() or 'sales' in table_name.lower():
                if not df.empty:
                    sales_df = df
                    break
        
        if sales_df is not None:
            # Create subplots for different analyses
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Sales amount distribution (if amount column exists)
            amount_cols = [col for col in sales_df.columns if 'amount' in col.lower() or 'value' in col.lower()]
            if amount_cols and sales_df[amount_cols[0]].notna().sum() > 0:
                sales_df[amount_cols[0]].hist(bins=50, ax=ax1, color='skyblue', alpha=0.7)
                ax1.set_title('Sales Amount Distribution', fontweight='bold')
                ax1.set_xlabel('Amount')
                ax1.set_ylabel('Frequency')
            else:
                ax1.text(0.5, 0.5, 'No amount data available', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Sales Amount Distribution', fontweight='bold')
            
            # 2. Top categories/customers (if category column exists)
            category_cols = [col for col in sales_df.columns if 'category' in col.lower() or 'type' in col.lower()]
            if category_cols:
                top_categories = sales_df[category_cols[0]].value_counts().head(10)
                top_categories.plot(kind='bar', ax=ax2, color='lightgreen', alpha=0.8)
                ax2.set_title('Top Categories/Types', fontweight='bold')
                ax2.tick_params(axis='x', rotation=45)
            else:
                ax2.text(0.5, 0.5, 'No category data available', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Top Categories/Types', fontweight='bold')
            
            # 3. Data completeness
            completeness = (sales_df.notna().sum() / len(sales_df) * 100).sort_values(ascending=False)
            completeness.head(10).plot(kind='barh', ax=ax3, color='orange', alpha=0.7)
            ax3.set_title('Data Completeness by Column (%)', fontweight='bold')
            ax3.set_xlabel('Completeness %')
            
            # 4. Record count over time (if date column exists)
            date_cols = [col for col in sales_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                try:
                    sales_df[date_cols[0]] = pd.to_datetime(sales_df[date_cols[0]], errors='coerce')
                    monthly_counts = sales_df.groupby(sales_df[date_cols[0]].dt.to_period('M')).size()
                    if len(monthly_counts) > 1:
                        monthly_counts.plot(ax=ax4, color='purple', marker='o')
                        ax4.set_title('Records Over Time', fontweight='bold')
                        ax4.set_xlabel('Period')
                        ax4.set_ylabel('Count')
                    else:
                        ax4.text(0.5, 0.5, 'Insufficient time data', ha='center', va='center', transform=ax4.transAxes)
                        ax4.set_title('Records Over Time', fontweight='bold')
                except:
                    ax4.text(0.5, 0.5, 'Date parsing failed', ha='center', va='center', transform=ax4.transAxes)
                    ax4.set_title('Records Over Time', fontweight='bold')
            else:
                ax4.text(0.5, 0.5, 'No date columns found', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Records Over Time', fontweight='bold')
            
            plt.suptitle('Sales Data Analysis', fontsize=16, fontweight='bold')
            plt.tight_layout()
        else:
            # Fallback: Show column type distribution across all tables
            plt.figure(figsize=(12, 8))
            all_columns = []
            for df in dataframes.values():
                all_columns.extend(df.dtypes.values)
            
            type_counts = pd.Series(all_columns).astype(str).value_counts()
            type_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.title('Column Data Types Distribution Across All Tables', fontsize=14, fontweight='bold')
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  📈 Created chart: {output_path}")
    
    def create_data_quality_chart(self, all_stats, output_path):
        """Create data quality overview chart."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Chart 1: Null values by table
        table_names = []
        null_counts = []
        for table, stats in all_stats.items():
            table_names.append(table.replace('dbo_', ''))
            null_counts.append(sum(stats['nulls'].values()))
        
        colors1 = plt.cm.Reds(np.linspace(0.3, 0.8, len(table_names)))
        bars1 = ax1.bar(range(len(table_names)), null_counts, color=colors1, alpha=0.8)
        ax1.set_title('Missing Values by Table', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Tables')
        ax1.set_ylabel('Number of Missing Values')
        ax1.set_xticks(range(len(table_names)))
        ax1.set_xticklabels(table_names, rotation=45, ha='right')
        
        # Add value labels
        for bar, count in zip(bars1, null_counts):
            if count > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(null_counts)*0.01,
                        f'{count}', ha='center', va='bottom', fontsize=9)
        
        # Chart 2: Column types distribution
        all_numeric_cols = sum(len(stats['numeric_columns']) for stats in all_stats.values())
        all_text_cols = sum(len(stats['text_columns']) for stats in all_stats.values())
        
        labels = ['Numeric Columns', 'Text Columns']
        sizes = [all_numeric_cols, all_text_cols]
        colors2 = ['lightblue', 'lightcoral']
        
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors2, startangle=90)
        ax2.set_title('Column Types Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"  🔍 Created chart: {output_path}")
    
    def create_html_report(self, insights, charts):
        """Create professional HTML report with embedded images."""
        import base64
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert images to base64 for embedding
        def image_to_base64(image_path):
            if os.path.exists(image_path):
                with open(image_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            return ""
        
        chart1_b64 = image_to_base64(charts[0]) if len(charts) > 0 else ""
        chart2_b64 = image_to_base64(charts[1]) if len(charts) > 1 else ""
        chart3_b64 = image_to_base64(charts[2]) if len(charts) > 2 else ""
        
        # Create HTML with embedded images
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Analysis Report - AI CODEFIX 2025</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .content {{
            padding: 40px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        .summary-card h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .insights {{
            background: #e8f5e8;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        .insights h2 {{
            color: #27ae60;
            margin-top: 0;
        }}
        .insights ul {{
            list-style: none;
            padding: 0;
        }}
        .insights li {{
            padding: 10px 0;
            border-bottom: 1px solid #d5eddb;
        }}
        .insights li:last-child {{
            border-bottom: none;
        }}
        .chart-section {{
            margin: 40px 0;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        .chart-container h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .recommendations {{
            background: #fff3cd;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
            margin: 30px 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #2c3e50;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Database Analysis Report</h1>
            <p>AI CODEFIX 2025 • {now}</p>
        </div>
        
        <div class="content">
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Analysis Date</h3>
                    <p>{now}</p>
                </div>
                <div class="summary-card">
                    <h3>Database</h3>
                    <p>Sales Agent Database</p>
                </div>
                <div class="summary-card">
                    <h3>Status</h3>
                    <p>✅ Complete</p>
                </div>
            </div>

            <div class="insights">
                <h2>🔍 Key Insights</h2>
                <ul>"""
        
        for insight in insights:
            html_content += f"<li>• {insight}</li>"
        
        html_content += """
                </ul>
            </div>

            <div class="chart-section">
                <h2>📊 Data Visualizations</h2>"""
        
        if chart1_b64:
            html_content += f"""
                <div class="chart-container">
                    <h3>📈 Table Size Distribution</h3>
                    <img src="data:image/png;base64,{chart1_b64}" alt="Table Distribution Chart">
                </div>"""
        
        if chart2_b64:
            html_content += f"""
                <div class="chart-container">
                    <h3>💰 Sales Analysis Dashboard</h3>
                    <img src="data:image/png;base64,{chart2_b64}" alt="Sales Analysis Chart">
                </div>"""
        
        if chart3_b64:
            html_content += f"""
                <div class="chart-container">
                    <h3>🔍 Data Quality Overview</h3>
                    <img src="data:image/png;base64,{chart3_b64}" alt="Data Quality Chart">
                </div>"""
        
        html_content += """
            </div>

            <div class="recommendations">
                <h2>💡 Recommendations</h2>
                <p>• Data quality appears good with comprehensive business intelligence structure</p>
                <p>• Continue monitoring for business insights and trend analysis</p>
                <p>• Consider addressing missing values in high-volume transaction tables</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Database Insights Agent • AI CODEFIX 2025</p>
        </div>
    </div>
</body>
</html>"""
        
        report_path = os.path.join(self.output_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"📄 Created report: {report_path}")
        
        # Also create PDF version
        pdf_path = self.create_pdf_report(html_content)
        return report_path, pdf_path
    
    def create_pdf_report(self, html_content):
        """Create PDF version of the report."""
        try:
            import pdfkit
            import shutil
            
            # Check for wkhtmltopdf
            wk_path = os.environ.get("WKHTMLTOPDF_PATH") or shutil.which("wkhtmltopdf")
            if not wk_path:
                print("⚠️ wkhtmltopdf not found - PDF generation skipped")
                return None
            
            config = pdfkit.configuration(wkhtmltopdf=wk_path)
            options = {
                "page-size": "A4",
                "margin-top": "0.75in",
                "margin-right": "0.75in",
                "margin-bottom": "0.75in",
                "margin-left": "0.75in",
                "encoding": "UTF-8",
                "no-outline": None,
                "enable-local-file-access": None
            }
            
            pdf_path = os.path.join(self.output_dir, "database_analysis_report.pdf")
            pdfkit.from_string(html_content, pdf_path, configuration=config, options=options)
            print(f"📄 Created PDF report: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"⚠️ PDF generation failed: {e}")
            return None
    
    def generate_detailed_analysis(self, all_stats, dataframes):
        """Generate comprehensive detailed analysis for email."""
        analysis = []
        
        # Database Overview
        total_tables = len(all_stats)
        total_records = sum(stat['total_rows'] for stat in all_stats.values())
        total_columns = sum(stat['columns'] for stat in all_stats.values())
        
        analysis.append(f"📊 DATABASE OVERVIEW:")
        analysis.append(f"   • Total Tables: {total_tables}")
        analysis.append(f"   • Total Records: {total_records:,}")
        analysis.append(f"   • Total Columns: {total_columns}")
        analysis.append(f"   • Database Size: ~{os.path.getsize(self.db_path) / (1024*1024):.1f} MB")
        analysis.append("")
        
        # Table-by-table breakdown
        analysis.append("🗂️ TABLE BREAKDOWN:")
        for table, stats in sorted(all_stats.items(), key=lambda x: x[1]['total_rows'], reverse=True):
            analysis.append(f"   📋 {table}:")
            analysis.append(f"      → Records: {stats['total_rows']:,}")
            analysis.append(f"      → Columns: {stats['columns']}")
            analysis.append(f"      → Numeric Fields: {len(stats['numeric_columns'])}")
            analysis.append(f"      → Text Fields: {len(stats['text_columns'])}")
            
            # Data quality for this table
            null_count = sum(stats['nulls'].values())
            if null_count > 0:
                analysis.append(f"      → Missing Values: {null_count:,} ({(null_count/(stats['total_rows']*stats['columns'])*100):.1f}%)")
            
            if stats['duplicates'] > 0:
                analysis.append(f"      → Duplicates: {stats['duplicates']} ({(stats['duplicates']/stats['total_rows']*100):.1f}%)")
            
            analysis.append("")
        
        # Data Quality Summary
        total_nulls = sum(sum(stats['nulls'].values()) for stats in all_stats.values())
        total_duplicates = sum(stats['duplicates'] for stats in all_stats.values())
        
        analysis.append("🔍 DATA QUALITY ASSESSMENT:")
        analysis.append(f"   • Total Missing Values: {total_nulls:,}")
        analysis.append(f"   • Total Duplicate Rows: {total_duplicates:,}")
        
        # Identify problematic tables
        high_null_tables = [(name, sum(stats['nulls'].values())) for name, stats in all_stats.items() 
                           if sum(stats['nulls'].values()) > 1000]
        if high_null_tables:
            analysis.append(f"   • Tables with High Missing Values:")
            for table, nulls in high_null_tables:
                analysis.append(f"     - {table}: {nulls:,} missing values")
        
        analysis.append("")
        
        # Business Intelligence Insights
        analysis.append("💰 BUSINESS INTELLIGENCE INSIGHTS:")
        
        # Customer analysis
        customer_tables = [name for name in all_stats.keys() if 'customer' in name.lower()]
        if customer_tables:
            total_customers = sum(all_stats[table]['total_rows'] for table in customer_tables)
            analysis.append(f"   • Customer Data: {len(customer_tables)} tables, {total_customers:,} customer records")
        
        # Sales analysis
        sales_tables = [name for name in all_stats.keys() if any(word in name.lower() for word in ['sales', 'transaction', 'order'])]
        if sales_tables:
            total_sales_records = sum(all_stats[table]['total_rows'] for table in sales_tables)
            analysis.append(f"   • Sales Data: {len(sales_tables)} tables, {total_sales_records:,} transaction records")
        
        # Find largest transaction table for analysis
        largest_sales_table = None
        max_sales_records = 0
        for name, stats in all_stats.items():
            if any(word in name.lower() for word in ['transaction', 'sales']) and stats['total_rows'] > max_sales_records:
                max_sales_records = stats['total_rows']
                largest_sales_table = name
        
        if largest_sales_table and largest_sales_table in dataframes:
            df = dataframes[largest_sales_table]
            # Analyze numeric columns in sales data
            amount_cols = [col for col in df.columns if any(word in col.lower() for word in ['amount', 'value', 'price', 'total'])]
            if amount_cols:
                analysis.append(f"   • Transaction Analysis ({largest_sales_table}):")
                for col in amount_cols[:3]:  # Top 3 amount columns
                    if df[col].notna().sum() > 0:
                        avg_amount = df[col].mean()
                        total_amount = df[col].sum()
                        analysis.append(f"     - {col}: Avg ${avg_amount:,.2f}, Total ${total_amount:,.2f}")
        
        analysis.append("")
        
        # Technical Recommendations
        analysis.append("🔧 TECHNICAL RECOMMENDATIONS:")
        
        # Data quality recommendations
        if total_nulls > 10000:
            analysis.append(f"   • HIGH PRIORITY: Address {total_nulls:,} missing values across tables")
        
        if total_duplicates > 100:
            analysis.append(f"   • MEDIUM PRIORITY: Remove {total_duplicates:,} duplicate records")
        
        # Performance recommendations
        large_tables = [(name, stats['total_rows']) for name, stats in all_stats.items() if stats['total_rows'] > 100000]
        if large_tables:
            analysis.append(f"   • PERFORMANCE: Consider indexing for {len(large_tables)} large tables (>100K records)")
        
        # Schema recommendations
        text_heavy_tables = [(name, len(stats['text_columns'])) for name, stats in all_stats.items() 
                           if len(stats['text_columns']) > 20]
        if text_heavy_tables:
            analysis.append(f"   • SCHEMA: Review text-heavy tables for normalization opportunities")
        
        analysis.append("")
        analysis.append("📈 NEXT STEPS:")
        analysis.append("   1. Review data quality issues highlighted above")
        analysis.append("   2. Implement automated data validation processes")
        analysis.append("   3. Set up regular monitoring for key business metrics")
        analysis.append("   4. Consider data warehousing for better analytics performance")
        
        return "\n".join(analysis)
    
    def send_email(self, recipient, report_files, chart_files, detailed_analysis):
        """Send professional email with attachments."""
        print(f"📧 Preparing to send email to {recipient}")
        
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        if not all([sender_email, sender_password]):
            print("❌ Email credentials not found. Report saved locally.")
            return False
        
        # Create email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = "Database Analysis Report - AI CODEFIX 2025"
        
        # Detailed email body with comprehensive analysis
        body = f"""Dear Recipient,

Please find the comprehensive automated database analysis report attached.

=== EXECUTIVE SUMMARY ===
- Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Database: Sales Agent Database (sales_agent.db)
- Analysis Status: ✅ COMPLETE
- Report Format: HTML + PDF + Visualizations

{detailed_analysis}

=== ATTACHED FILES ===
📄 database_analysis_report.pdf - Complete analysis report (PDF format)
🌐 report.html - Interactive HTML report with embedded charts
📊 chart_table_distribution.png - Database structure visualization
📈 chart_sales_analysis.png - Sales performance dashboard
🔍 chart_data_quality.png - Data quality assessment

=== REPORT HIGHLIGHTS ===
✅ Comprehensive database schema analysis
✅ Business intelligence insights and recommendations
✅ Data quality assessment with actionable findings
✅ Professional visualizations and trend analysis
✅ Technical recommendations for optimization

This analysis provides actionable insights for:
→ Data quality improvement initiatives
→ Business intelligence and reporting strategies  
→ Database optimization and performance tuning
→ Strategic decision-making based on data patterns

For technical questions or follow-up analysis, please contact our data team.

Best regards,
Database Insights Agent
AI CODEFIX 2025

---
🔒 This report contains business-sensitive data. Please handle according to your organization's data governance policies."""
        
        msg.attach(MIMEText(body, "plain"))
        
        # Attach files (HTML, PDF, and charts)
        if isinstance(report_files, tuple):
            html_file, pdf_file = report_files
            if os.path.exists(html_file):
                self.attach_file(msg, html_file)
            if pdf_file and os.path.exists(pdf_file):
                self.attach_file(msg, pdf_file)
        else:
            if os.path.exists(report_files):
                self.attach_file(msg, report_files)
        
        # Attach chart files
        for file_path in chart_files:
            if os.path.exists(file_path):
                self.attach_file(msg, file_path)
        
        # Send email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [recipient], msg.as_string())
            print(f"✅ Email sent successfully to {recipient}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}. Report saved locally.")
            return False
    
    def attach_file(self, msg, file_path):
        """Attach file to email."""
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        
        maintype, subtype = ctype.split("/", 1)
        with open(file_path, "rb") as fp:
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(file_path)}"'
            )
            msg.attach(attachment)
    
    def run_analysis(self, recipient_email):
        """Run the complete analysis pipeline."""
        print("🚀 Starting Database Analysis...")
        
        try:
            # Discover tables
            tables = self.discover_tables()
            print(f"🔍 Found {len(tables)} tables")
            
            # Analyze tables (sample large ones)
            all_stats = {}
            dataframes = {}
            
            for table in tables:
                df, stats = self.analyze_table(table)
                all_stats[table] = stats
                dataframes[table] = df
            
            # Generate insights
            print("💡 Generating insights...")
            insights = self.generate_insights(all_stats)
            
            # Create visualizations
            print("📊 Creating visualizations...")
            charts = self.create_visualizations(all_stats, dataframes)
            
            # Generate detailed analysis for email
            print("📊 Generating detailed analysis...")
            detailed_analysis = self.generate_detailed_analysis(all_stats, dataframes)
            
            # Create report (HTML + PDF)
            print("📄 Creating reports...")
            report_files = self.create_html_report(insights, charts)
            
            # Send email with detailed analysis
            self.send_email(recipient_email, report_files, charts, detailed_analysis)
            
            print("✅ Analysis completed successfully!")
            print(f"📁 Files saved in: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.conn.close()

def main():
    parser = argparse.ArgumentParser(description="Database Insights Agent - AI CODEFIX 2025")
    parser.add_argument("--db", required=True, help="Path to SQLite database file")
    parser.add_argument("--email", required=True, help="Recipient email address")
    args = parser.parse_args()
    
    analyzer = DatabaseAnalyzer(args.db)
    analyzer.run_analysis(args.email)

if __name__ == "__main__":
    main()