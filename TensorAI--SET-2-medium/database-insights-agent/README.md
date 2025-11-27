# Database Insights Agent

## Overview

The Database Insights Agent is a Python application designed to analyze a SQLite database, generate insightful reports, and automate the process of sending these reports via email. This project leverages various libraries for data analysis, visualization, and email automation.

## Project Structure

```
database-insights-agent/
├── src/
│   ├── db_analyzer.py          # Main script for analysis and reporting
│   ├── analyzer/                # Module for database analysis
│   │   ├── __init__.py          # Initializes the analyzer module
│   │   ├── db_reader.py         # Functions to read data from the database
│   │   ├── analysis.py          # Functions for data analysis
│   │   ├── viz.py               # Functions for generating visualizations
│   │   └── report.py            # Functions for creating reports
│   ├── email/                   # Module for email functionality
│   │   ├── __init__.py          # Initializes the email module
│   │   └── sender.py            # Functions for sending emails
│   ├── templates/               # HTML templates for reports
│   │   └── report_template.html  # Template for the report
│   └── config.py                # Configuration settings
├── data/                        # Directory for data files
│   └── data.db                  # SQLite database file
├── tests/                       # Directory for unit tests
│   ├── test_db_reader.py        # Tests for db_reader module
│   └── test_analysis.py         # Tests for analysis module
├── output/                      # Directory for output files
│   └── reports                  # Generated reports
├── requirements.txt             # Project dependencies
├── .env.example                 # Example environment variables
└── README.md                    # Project documentation
```

## Features

- **Database Analysis**: Connects to a SQLite database, reads data, and performs statistical analysis.
- **Data Visualization**: Generates various types of charts and graphs to visualize data insights.
- **Report Generation**: Compiles analysis results and visualizations into a professional report format (HTML or PDF).
- **Email Automation**: Automatically sends the generated report via email to specified recipients.

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd database-insights-agent
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Create a `.env` file based on `.env.example` and fill in the required credentials.

4. **Run the application**:
   ```
   python src/db_analyzer.py --db data/data.db --email recipient@example.com
   ```

## Usage

- The main script `db_analyzer.py` is responsible for orchestrating the entire process from database connection to report generation and email sending.
- The `analyzer` module contains the core logic for reading data, performing analysis, and generating visualizations.
- The `email` module handles the formatting and sending of emails with the generated reports.

## Contribution

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.