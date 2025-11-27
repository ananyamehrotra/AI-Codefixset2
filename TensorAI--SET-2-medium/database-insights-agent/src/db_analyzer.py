import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from analyzer.db_reader import read_data
from analyzer.analysis import perform_analysis
from analyzer.viz import generate_visualizations
from analyzer.report import create_report
from emaill.sender import send_email
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def main(database_path, recipient_email):
    try:
        print(f"🗃️  Connecting to database: {database_path}")
        # Connect to the database and read data
        conn = sqlite3.connect(database_path)
        dataframes = read_data(conn)

        # Perform analysis
        insights = perform_analysis(dataframes)

        # Generate visualizations
        visualization_files = generate_visualizations(insights)

        # Create report
        report_file = create_report(insights, visualization_files)

        # Send email with the report
        subject = "Database Analysis Report - AI CODEFIX 2025"
        body = f"""Dear Recipient,

Please find the automated database analysis report attached.

=== DATABASE SUMMARY ===
- Total Tables: {len(insights['summary'])}
- Total Records: {sum(table['rows'] for table in insights['summary'].values()):,}
- Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

=== KEY INSIGHTS ===
{chr(10).join([f'{i+1}. {finding}' for i, finding in enumerate(insights['key_findings'])])}

Best regards,
Database Insights Agent
AI CODEFIX 2025"""
        
        attachments = [report_file] + visualization_files
        send_email(subject, body, recipient_email, attachments)
        
        conn.close()
        print("✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Database Insights Agent')
    parser.add_argument('--db', required=True, help='Path to the SQLite database file')
    parser.add_argument('--email', required=True, help='Recipient email address')
    args = parser.parse_args()

    main(args.db, args.email)