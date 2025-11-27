from jinja2 import Environment, FileSystemLoader
import os

def generate_report(analysis_summary, visualizations):
    # Load the HTML template
    env = Environment(loader=FileSystemLoader('src/templates'))
    template = env.get_template('report_template.html')

    # Create the report content
    report_content = template.render(
        analysis_summary=analysis_summary,
        visualizations=visualizations
    )

    return report_content

def save_report(report_content, output_path):
    # Save the report to a file
    with open(output_path, 'w') as report_file:
        report_file.write(report_content)

def generate_pdf_report(report_content, output_path):
    # Convert HTML to PDF (implementation depends on the library used)
    # This is a placeholder for actual PDF generation logic
    pass

def create_report(insights, visualization_files, output_format='html'):
    """Create HTML and PDF report from insights and visualizations."""
    print("📄 Creating report...")
    
    try:
        # Setup Jinja2 environment
        template_dir = os.path.join("..", "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report_template.html")
        
        # Prepare data for template
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_tables = len(insights['summary'])
        total_records = sum(table_info['rows'] for table_info in insights['summary'].values())
        
        # Generate insights text
        insight_1 = insights['key_findings'][0] if len(insights['key_findings']) > 0 else "No specific insights available"
        insight_2 = insights['key_findings'][1] if len(insights['key_findings']) > 1 else "Data analysis completed successfully"
        insight_3 = insights['key_findings'][2] if len(insights['key_findings']) > 2 else "Additional analysis may reveal more patterns"
        
        # Generate recommendations
        recommendations = generate_recommendations(insights)
        
        # Chart filenames (just the basename for HTML)
        chart1 = os.path.basename(visualization_files[0]) if len(visualization_files) > 0 else ""
        chart2 = os.path.basename(visualization_files[1]) if len(visualization_files) > 1 else ""
        chart3 = os.path.basename(visualization_files[2]) if len(visualization_files) > 2 else ""
        
        # Render template
        html_content = template.render(
            analysis_date=now,
            total_tables=total_tables,
            total_records=f"{total_records:,}",
            insight_1=insight_1,
            insight_2=insight_2,
            insight_3=insight_3,
            chart1=chart1,
            chart2=chart2,
            chart3=chart3,
            recommendations=recommendations
        )
        
        # Save HTML report
        output_dir = os.path.join("..", "output", "reports")
        os.makedirs(output_dir, exist_ok=True)
        html_path = os.path.join(output_dir, "report.html")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ HTML report created: {html_path}")
        return html_path
            
    except Exception as e:
        print(f"❌ Error creating report: {e}")
        # Fallback: create simple text report
        return create_simple_text_report(insights, visualization_files)

def generate_recommendations(insights):
    """Generate actionable recommendations based on insights."""
    recommendations = []
    
    try:
        # Check for data quality issues
        for table, quality in insights['data_quality'].items():
            null_count = sum(quality['null_counts'].values())
            if null_count > 0:
                recommendations.append(f"Address missing data in '{table}' table")
            
            if quality['duplicate_rows'] > 0:
                recommendations.append(f"Remove {quality['duplicate_rows']} duplicate rows from '{table}'")
        
        if not recommendations:
            recommendations.append("Data quality appears good - continue monitoring for changes")
        
    except Exception as e:
        print(f"Warning: Error generating recommendations: {e}")
        recommendations.append("Manual review recommended")
    
    return " | ".join(recommendations)

def create_simple_text_report(insights, visualization_files):
    """Create a simple text report as fallback."""
    output_dir = os.path.join("..", "output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    text_path = os.path.join(output_dir, "report.txt")
    
    import datetime
    with open(text_path, "w", encoding="utf-8") as f:
        f.write("DATABASE ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Tables: {len(insights['summary'])}\n")
        total_records = sum(table_info['rows'] for table_info in insights['summary'].values())
        f.write(f"Total Records: {total_records:,}\n\n")
        
        # Key Findings
        f.write("KEY FINDINGS\n")
        f.write("-" * 20 + "\n")
        for i, finding in enumerate(insights['key_findings'], 1):
            f.write(f"{i}. {finding}\n")
        f.write("\n")
        
        # Table Details
        f.write("TABLE DETAILS\n")
        f.write("-" * 20 + "\n")
        for table, info in insights['summary'].items():
            f.write(f"{table}: {info['rows']} rows, {info['columns']} columns\n")
        
        f.write(f"\nVisualization files: {len(visualization_files)} charts created\n")
    
    print(f"✅ Text report created: {text_path}")
    return text_path