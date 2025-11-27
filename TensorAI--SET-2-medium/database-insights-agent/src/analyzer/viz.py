import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Set matplotlib backend for server environments
plt.switch_backend('Agg')

def generate_visualizations(insights):
    """Generate visualizations based on the analysis insights."""
    print("📊 Generating visualizations...")
    
    viz_files = []
    output_dir = os.path.join("..", "output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Chart 1: Table size comparison
        chart1_path = os.path.join(output_dir, "chart_table_sizes.png")
        if create_table_size_chart(insights, chart1_path):
            viz_files.append(chart1_path)
        
        # Chart 2: Data quality overview
        chart2_path = os.path.join(output_dir, "chart_data_quality.png")
        if create_data_quality_chart(insights, chart2_path):
            viz_files.append(chart2_path)
        
        # Chart 3: Statistics overview (if numeric data exists)
        chart3_path = os.path.join(output_dir, "chart_statistics.png")
        if create_statistics_chart(insights, chart3_path):
            viz_files.append(chart3_path)
        
        print(f"✅ Generated {len(viz_files)} visualizations")
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
    
    return viz_files

def create_table_size_chart(insights, output_path):
    """Create a bar chart showing table sizes."""
    try:
        if not insights['summary']:
            print("No summary data available for table size chart")
            return False
            
        table_names = list(insights['summary'].keys())
        row_counts = [insights['summary'][table]['rows'] for table in table_names]
        
        # Create figure
        plt.figure(figsize=(12, 7))
        
        # Create bar chart with colors
        colors = plt.cm.Set3(np.linspace(0, 1, len(table_names)))
        bars = plt.bar(table_names, row_counts, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Customize chart
        plt.title('Number of Records by Table', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Tables', fontsize=12)
        plt.ylabel('Number of Records', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, count in zip(bars, row_counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(row_counts)*0.01,
                    f'{count:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"  ✅ Created table size chart: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating table size chart: {e}")
        plt.close()
        return False

def create_data_quality_chart(insights, output_path):
    """Create a chart showing data quality metrics."""
    try:
        if not insights['data_quality']:
            print("No data quality information available")
            return False
            
        tables = list(insights['data_quality'].keys())
        null_counts = [sum(insights['data_quality'][table]['null_counts'].values()) for table in tables]
        duplicate_counts = [insights['data_quality'][table]['duplicate_rows'] for table in tables]
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Null values chart
        colors1 = plt.cm.Oranges(np.linspace(0.4, 0.8, len(tables)))
        bars1 = ax1.bar(tables, null_counts, color=colors1, alpha=0.8, edgecolor='black', linewidth=0.5)
        ax1.set_title('Null Values by Table', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Tables', fontsize=11)
        ax1.set_ylabel('Number of Null Values', fontsize=11)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels for null chart
        for bar, count in zip(bars1, null_counts):
            if count > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(null_counts)*0.01,
                        f'{count}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Duplicate rows chart
        colors2 = plt.cm.Reds(np.linspace(0.4, 0.8, len(tables)))
        bars2 = ax2.bar(tables, duplicate_counts, color=colors2, alpha=0.8, edgecolor='black', linewidth=0.5)
        ax2.set_title('Duplicate Rows by Table', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Tables', fontsize=11)
        ax2.set_ylabel('Number of Duplicate Rows', fontsize=11)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels for duplicate chart
        for bar, count in zip(bars2, duplicate_counts):
            if count > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(duplicate_counts)*0.01,
                        f'{count}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"  ✅ Created data quality chart: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating data quality chart: {e}")
        plt.close()
        return False

def create_statistics_chart(insights, output_path):
    """Create a chart showing statistical distributions."""
    try:
        # Check if we have any statistical data
        if not insights['statistics']:
            print("No statistical data available for charts")
            return False
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        chart_created = False
        chart_idx = 0
        
        for table_name, stats in insights['statistics'].items():
            if chart_idx >= 4:  # Max 4 subplots
                break
                
            if stats:  # If we have statistics for this table
                # Get first numeric column statistics
                first_col = list(stats.keys())[0]
                col_stats = stats[first_col]
                
                # Create a bar chart of key statistics
                stat_names = ['mean', 'std', 'min', '25%', '50%', '75%', 'max']
                stat_values = [col_stats.get(stat, 0) for stat in stat_names]
                
                # Filter out any non-numeric values
                valid_stats = []
                valid_names = []
                for name, value in zip(stat_names, stat_values):
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        valid_stats.append(value)
                        valid_names.append(name)
                
                if valid_stats:
                    colors = plt.cm.viridis(np.linspace(0, 1, len(valid_stats)))
                    bars = axes[chart_idx].bar(valid_names, valid_stats, color=colors, alpha=0.8)
                    axes[chart_idx].set_title(f'{table_name} - {first_col}', fontsize=12, fontweight='bold')
                    axes[chart_idx].tick_params(axis='x', rotation=45)
                    axes[chart_idx].grid(axis='y', alpha=0.3, linestyle='--')
                    
                    # Add value labels
                    for bar, value in zip(bars, valid_stats):
                        axes[chart_idx].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valid_stats)*0.01,
                                f'{value:.2f}', ha='center', va='bottom', fontsize=9)
                    
                    chart_created = True
                    chart_idx += 1
        
        # Hide unused subplots
        for i in range(chart_idx, 4):
            axes[i].set_visible(False)
        
        if chart_created:
            plt.suptitle('Statistical Overview by Table', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            print(f"  ✅ Created statistics chart: {output_path}")
            return True
        else:
            plt.close()
            print("  ⚠️ No valid statistics data for chart creation")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating statistics chart: {e}")
        plt.close()
        return False

def create_correlation_heatmap(dataframes, output_path):
    """Create correlation heatmap for numeric columns."""
    try:
        # Find the table with the most numeric columns
        best_table = None
        max_numeric_cols = 0
        
        for table_name, df in dataframes.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > max_numeric_cols:
                max_numeric_cols = len(numeric_cols)
                best_table = (table_name, df)
        
        if best_table and max_numeric_cols >= 2:
            table_name, df = best_table
            numeric_df = df.select_dtypes(include=[np.number])
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            
            # Create heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
            plt.title(f'Correlation Matrix - {table_name}', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"  ✅ Created correlation heatmap: {output_path}")
            return True
        else:
            print("  ⚠️ Insufficient numeric data for correlation heatmap")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating correlation heatmap: {e}")
        plt.close()
        return False

def create_distribution_plots(dataframes, output_path):
    """Create distribution plots for numeric columns."""
    try:
        # Find numeric columns across all tables
        numeric_data = []
        column_info = []
        
        for table_name, df in dataframes.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols[:2]:  # Limit to 2 columns per table
                if not df[col].empty and df[col].notna().sum() > 0:
                    numeric_data.append(df[col].dropna())
                    column_info.append(f"{table_name}.{col}")
        
        if numeric_data:
            n_plots = min(len(numeric_data), 4)  # Max 4 plots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            axes = axes.flatten()
            
            for i in range(n_plots):
                data = numeric_data[i]
                axes[i].hist(data, bins=30, alpha=0.7, edgecolor='black', linewidth=0.5)
                axes[i].set_title(f'Distribution: {column_info[i]}', fontsize=11, fontweight='bold')
                axes[i].set_xlabel('Values')
                axes[i].set_ylabel('Frequency')
                axes[i].grid(axis='y', alpha=0.3, linestyle='--')
            
            # Hide unused subplots
            for i in range(n_plots, 4):
                axes[i].set_visible(False)
            
            plt.suptitle('Data Distributions', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"  ✅ Created distribution plots: {output_path}")
            return True
        else:
            print("  ⚠️ No numeric data available for distribution plots")
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating distribution plots: {e}")
        plt.close()
        return False