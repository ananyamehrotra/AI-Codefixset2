import pandas as pd
import numpy as np

def perform_analysis(dataframes):
    """Perform comprehensive analysis on the dataframes."""
    print("🔍 Starting data analysis...")
    
    insights = {
        'summary': {},
        'statistics': {},
        'data_quality': {},
        'key_findings': []
    }
    
    if not dataframes:
        print("❌ No dataframes provided for analysis")
        return insights
    
    # Summary statistics
    print("📊 Calculating summary statistics...")
    for table_name, df in dataframes.items():
        insights['summary'][table_name] = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'column_names': list(df.columns)
        }
        
        # Detailed statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights['statistics'][table_name] = df[numeric_cols].describe().to_dict()
        
        # Data quality checks
        insights['data_quality'][table_name] = {
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': int(df.duplicated().sum()),
            'unique_values_per_column': {col: int(df[col].nunique()) for col in df.columns}
        }
        
        print(f"  ✅ Analyzed {table_name}: {len(df)} rows, {len(df.columns)} columns")
    
    # Generate key findings
    print("💡 Generating key insights...")
    insights['key_findings'] = generate_key_findings(dataframes, insights)
    
    print("✅ Analysis complete!")
    return insights

def generate_key_findings(dataframes, insights):
    """Generate key insights and findings."""
    findings = []
    
    try:
        # Find largest table
        if insights['summary']:
            largest_table = max(insights['summary'].items(), key=lambda x: x[1]['rows'])
            findings.append(f"Largest table is <b>{largest_table[0]}</b> with {largest_table[1]['rows']:,} records")
        
        # Calculate total records
        total_records = sum(info['rows'] for info in insights['summary'].values())
        findings.append(f"Total records across all tables: <b>{total_records:,}</b>")
        
        # Data quality insights
        tables_with_nulls = []
        for table, quality in insights['data_quality'].items():
            null_count = sum(quality['null_counts'].values())
            if null_count > 0:
                tables_with_nulls.append(f"{table} ({null_count} nulls)")
        
        if tables_with_nulls:
            findings.append(f"Tables with missing data: <b>{', '.join(tables_with_nulls)}</b>")
        else:
            findings.append("No missing data detected in any table")
        
        # Duplicate detection
        tables_with_dupes = []
        for table, quality in insights['data_quality'].items():
            if quality['duplicate_rows'] > 0:
                tables_with_dupes.append(f"{table} ({quality['duplicate_rows']} duplicates)")
        
        if tables_with_dupes:
            findings.append(f"Tables with duplicate rows: <b>{', '.join(tables_with_dupes)}</b>")
        
        # Numeric analysis insights
        for table_name, df in dataframes.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                # Find column with highest values
                col = numeric_cols[0]
                total_value = df[col].sum()
                avg_value = df[col].mean()
                findings.append(f"In <b>{table_name}</b>, {col} total: {total_value:,.2f} (avg: {avg_value:,.2f})")
                break
        
    except Exception as e:
        print(f"Warning: Error generating some insights: {e}")
        findings.append("Analysis completed with basic insights")
    
    # Ensure we have at least 3 insights
    while len(findings) < 3:
        findings.append("Additional analysis recommended for deeper insights")
    
    return findings[:3]  # Return top 3 insights

def calculate_correlations(dataframes):
    """Calculate correlations between numeric columns."""
    correlations = {}
    
    for table_name, df in dataframes.items():
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) >= 2:
            correlations[table_name] = numeric_df.corr()
    
    return correlations

def detect_anomalies(dataframes):
    """Detect potential anomalies in the data."""
    anomalies = {}
    
    for table_name, df in dataframes.items():
        table_anomalies = []
        
        # Check for numeric anomalies using IQR method
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if len(outliers) > 0:
                table_anomalies.append({
                    'column': col,
                    'outlier_count': len(outliers),
                    'percentage': (len(outliers) / len(df)) * 100
                })
        
        if table_anomalies:
            anomalies[table_name] = table_anomalies
    
    return anomalies

def generate_data_profile(dataframes):
    """Generate a comprehensive data profile."""
    profile = {}
    
    for table_name, df in dataframes.items():
        table_profile = {
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'unique_counts': df.nunique().to_dict()
        }
        
        # Add sample data
        table_profile['sample_data'] = df.head().to_dict()
        
        profile[table_name] = table_profile
    
    return profile