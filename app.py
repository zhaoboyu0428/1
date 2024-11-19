import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Set page title, icon, and default layout
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon=":chart_with_upwards_trend:"
)

# Load CSS from an external file
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found. Please ensure 'styles.css' is in the correct location.")

# Apply the CSS
load_css("styles.css")

# Page title
st.title(":chart_with_upwards_trend: Stock Analysis Dashboard")

# Load data files
DATA_FILENAME = Path(__file__).parent / 'data' / 'SP600_AdjClose_Volume_Return.csv'
FULL_DATA_FILENAME = Path(__file__).parent / 'data' / 'full_table.csv'

# Load stock price data
stock_df = pd.read_csv(DATA_FILENAME)
stock_df.columns = stock_df.columns.str.strip()
stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce')
stock_df['Adj Close'] = pd.to_numeric(stock_df['Adj Close'], errors='coerce')
stock_df = stock_df.dropna(subset=['Date', 'Adj Close']).sort_values('Date')

# Load anomaly data from full_data.csv
full_data_df = pd.read_csv(FULL_DATA_FILENAME)
full_data_df.columns = full_data_df.columns.str.strip()
full_data_df['Date'] = pd.to_datetime(full_data_df['Date'], errors='coerce')
full_data_df = full_data_df.dropna(subset=['Date']).sort_values('Date')

# Set up the date range and ticker selection
min_date = stock_df['Date'].min()
max_date = stock_df['Date'].max()
start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)
ticker_list = stock_df['Ticker'].unique()
selected_ticker = st.selectbox("Select Stock Ticker", ticker_list)

# Model selection dropdown to filter anomalies
selected_model = st.selectbox("Select Model", ["baseline", "svm", "dbscan", "isolation tree"])

# Ensure start_date is before end_date
if start_date > end_date:
    st.error("Error: Start Date must be before End Date.")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Stock Price", "Anomaly Detection", "Model Explanation"])

    # Tab 1: Stock Price Visualization
    with tab1:
        st.header("Stock Price Visualization")

        # Filter stock data based on date range and ticker
        filtered_stock_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) &
                                     (stock_df['Date'] <= pd.to_datetime(end_date)) &
                                     (stock_df['Ticker'] == selected_ticker)]

        if not filtered_stock_df.empty:
            # Plot stock price trend
            line_chart = alt.Chart(filtered_stock_df).mark_line().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Adj Close:Q', title='Adjusted Close Price')
            ).properties(
                width=700,
                height=400,
                title=f"Stock Price Trend for {selected_ticker} ({start_date} - {end_date})"
            )
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.error("No data available for the selected date range and ticker.")

    # Tab 2: Anomaly Detection
    with tab2:
        st.header("Anomaly Detection")

        # Filter stock data based on date range and ticker
        filtered_stock_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) &
                                     (stock_df['Date'] <= pd.to_datetime(end_date)) &
                                     (stock_df['Ticker'] == selected_ticker)]

        # Filter anomaly data based on date range, ticker, and selected model
        filtered_anomaly_df = full_data_df[(full_data_df['Date'] >= pd.to_datetime(start_date)) &
                                           (full_data_df['Date'] <= pd.to_datetime(end_date)) &
                                           (full_data_df['Ticker'] == selected_ticker) &
                                           (full_data_df[selected_model] == 1)]  # Only anomalies for selected model

        # Merge anomaly data with stock price data to get 'Adj Close' for anomaly points
        merged_anomaly_df = pd.merge(filtered_anomaly_df, filtered_stock_df[['Date', 'Ticker', 'Adj Close']],
                                     on=['Date', 'Ticker'], how='inner')

        if not filtered_stock_df.empty:
            # Plot stock price trend
            line_chart = alt.Chart(filtered_stock_df).mark_line().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Adj Close:Q', title='Adjusted Close Price')
            )

            # Mark anomaly points if any
            if not merged_anomaly_df.empty:
                anomaly_points = alt.Chart(merged_anomaly_df).mark_circle(size=60, color='red').encode(
                    x='Date:T',
                    y='Adj Close:Q',
                    tooltip=['Date', 'Adj Close']
                )
                # Combine line chart and anomaly points
                combined_chart = (line_chart + anomaly_points).properties(
                    width=700,
                    height=400,
                    title=f"Stock Price with {selected_model.capitalize()} Anomalies for {selected_ticker} ({start_date} - {end_date})"
                )
            else:
                # If no anomalies, show only the line chart
                combined_chart = line_chart.properties(
                    width=700,
                    height=400,
                    title=f"Stock Price Trend for {selected_ticker} ({start_date} - {end_date})"
                )

            st.altair_chart(combined_chart, use_container_width=True)
        else:
            st.error("No data available for the selected date range and ticker.")

    # Tab 3: Model Explanation
    with tab3:
        st.header("Model Explanation")
        st.write("In this section, you can explain the model used for analysis.")

        st.subheader("Model Overview")
        st.write(f"""
        {selected_model.capitalize()} model is used to detect stock price anomalies by analyzing trends and unusual patterns.
        """)
        st.subheader("Key Features Used")
        st.write("""
        - Rolling mean and standard deviation of returns
        - Price momentum calculated from adjusted close prices
        - Volatility and volume trends
        """)
        st.subheader("Future Improvements")
        st.write("""
        Future enhancements could include additional feature engineering, more anomaly detection algorithms, and integrating real-time data.
        """)
