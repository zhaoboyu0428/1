import pandas as pd
from pathlib import Path

# Define file paths
ANOMALY_FILENAME = Path(__file__).parent / 'data' / 'overall_anomalies.csv'
SVM_ANOMALIES_FILENAME = Path(__file__).parent / 'data' / 'svm_anomalies.csv'
DBSCAN_ANOMALIES_FILENAME = Path(__file__).parent / 'data' / 'anomalies_dbscan_pca.csv'
ISOLATION_ANOMALIES_FILENAME = Path(__file__).parent / 'data' / 'all_stock_anomalies_5th_threshold.csv'

# Load data
overall_anomalies = pd.read_csv(ANOMALY_FILENAME)

overall_anomalies.rename(columns={'Overall_Anomaly': 'baseline'}, inplace=True)

# Load additional datasets
svm_anomalies = pd.read_csv(SVM_ANOMALIES_FILENAME)
dbscan_anomalies = pd.read_csv(DBSCAN_ANOMALIES_FILENAME)
isolation_anomalies = pd.read_csv(ISOLATION_ANOMALIES_FILENAME)

# Add 'svm_match' column: 1 if match, 0 otherwise
overall_anomalies['svm'] = overall_anomalies.merge(
    svm_anomalies[['Ticker', 'Date']], on=['Ticker', 'Date'], how='left', indicator=True
)['_merge'].eq('both').astype(int)

# Add 'dbscan_match' column: 1 if match, 0 otherwise
overall_anomalies['dbscan'] = overall_anomalies.merge(
    dbscan_anomalies[['Ticker', 'Date']], on=['Ticker', 'Date'], how='left', indicator=True
)['_merge'].eq('both').astype(int)

# Add 'isolation_match' column: 1 if match, 0 otherwise
overall_anomalies['isolation tree'] = overall_anomalies.merge(
    isolation_anomalies[['Ticker', 'Date']], on=['Ticker', 'Date'], how='left', indicator=True
)['_merge'].eq('both').astype(int)

# Define the output file path
output_file = Path(__file__).parent / 'data' / 'full_table.csv'

# Save the DataFrame to a CSV file
overall_anomalies.to_csv(output_file, index=False)

# Display first 50 rows to confirm
print(overall_anomalies.head(50))
