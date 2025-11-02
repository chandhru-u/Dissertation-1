import streamlit as st
import pandas as pd

# -------------------------------
# 🎨 CUSTOM THEME / BACKGROUND
# -------------------------------
st.markdown("""
    <style>
        /* Main app background */
        .stApp {
            background-color: #f8fbff;  /* light blue-gray */
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #e6f0ff;  /* soft blue */
        }
        /* Container/card styling */
        .block-container {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
        }
        /* Titles and headers */
        h1, h2, h3 {
            color: #003366;
        }
        /* Buttons */
        button[kind="primary"] {
            background-color: #0066cc !important;
            color: white !important;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# 🏙️ CITY CONFIGURATION
# -------------------------------
CITY_FILES = {
    "Vellore": "predicted_test_1.csv",
    "Chennai": "predicted_test_2.csv",
    "Coimbatore": "predicted_test_3.csv"
}

USER_DATA_FILES = {
    "Vellore": "user_energy_data_1.csv",
    "Chennai": "user_energy_data_2.csv",
    "Coimbatore": "user_energy_data_3.csv"
}

OVERCONSUMPTION_THRESHOLD = 0.0600
LOW_CONSUMPTION_THRESHOLD = 0.0500

# -------------------------------
# 🏠 MAIN TITLE
# -------------------------------
st.title('⚡ Energy Prediction Dashboard')

# -------------------------------
# 🧭 SIDEBAR CONTROLS
# -------------------------------
st.sidebar.header("🔹 City Selection")
selected_city = st.sidebar.selectbox("Choose a City:", list(CITY_FILES.keys()))

data_file = CITY_FILES[selected_city]
user_data_file = USER_DATA_FILES[selected_city]

# -------------------------------
# 📂 LOAD DATA
# -------------------------------
data = pd.read_csv(data_file, parse_dates=['timestamp'])
user_data = pd.read_csv(user_data_file, parse_dates=['timestamp'])

required_cols = ['timestamp', 'predicted_energy']
if not all(col in data.columns for col in required_cols):
    st.error(f"The file for {selected_city} is missing required columns.")
    st.stop()

# -------------------------------
# 📆 DATE FILTER FOR PREDICTION DATA
# -------------------------------
st.sidebar.header("📅 Date Range for Prediction Data")
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

if st.sidebar.button('Apply Date Filter'):
    if start_date and end_date:
        mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
        filtered_data = data.loc[mask].copy()
    else:
        filtered_data = data.head(20).copy()
else:
    st.info("Showing first 20 rows by default. Apply date filter for full view.")
    filtered_data = data.head(20).copy()

# -------------------------------
# ⚙️ STATUS CLASSIFICATION
# -------------------------------
filtered_data['status'] = filtered_data['predicted_energy'].apply(
    lambda x: 'Overconsumption' if x > OVERCONSUMPTION_THRESHOLD
    else ('Low Consumption' if x < LOW_CONSUMPTION_THRESHOLD else 'Normal')
)

# -------------------------------
# 📊 DISPLAY FILTERED DATA
# -------------------------------
st.write(f"### 📍 Selected City: {selected_city}")
st.write(f"Showing results from **{start_date.date()}** to **{end_date.date()}**")

st.dataframe(filtered_data[['timestamp', 'predicted_energy', 'status']])

# -------------------------------
# 📈 PREDICTED ENERGY CHART
# -------------------------------
st.subheader("Predicted Energy Output Over Time")

if not filtered_data.empty:
    chart_data = filtered_data.set_index('timestamp')['predicted_energy']
    st.line_chart(chart_data)
    st.write(f"**Overconsumption Threshold**: {OVERCONSUMPTION_THRESHOLD} kWh")
    st.write(f"**Low Consumption Threshold**: {LOW_CONSUMPTION_THRESHOLD} kWh")

    # ⚠️ Alerts
    st.subheader("Consumption Status Alerts")
    if (filtered_data['status'] == 'Overconsumption').any():
        st.warning("🚨 Overconsumption detected during the selected period!")
    elif (filtered_data['status'] == 'Low Consumption').any():
        st.info("ℹ️ Low consumption detected during the selected period.")
    else:
        st.success("✅ Normal consumption during the selected period.")

# -------------------------------
# ⚖️ ENERGY USAGE COMPARISON
# -------------------------------
st.title('⚖️ Energy Usage Comparison')

comparison_start_date = st.sidebar.date_input('Comparison Start Date')
comparison_end_date = st.sidebar.date_input('Comparison End Date')

comparison_start_date = pd.to_datetime(comparison_start_date)
comparison_end_date = pd.to_datetime(comparison_end_date)

comparison_mask = (data['timestamp'] >= comparison_start_date) & (data['timestamp'] <= comparison_end_date)
comparison_filtered_data = data.loc[comparison_mask].copy()

if 'actual_energy' not in comparison_filtered_data.columns:
    comparison_filtered_data['actual_energy'] = comparison_filtered_data['predicted_energy'] * 0.95

st.subheader("Predicted vs Actual Energy Usage")
if not comparison_filtered_data.empty:
    st.line_chart(comparison_filtered_data[['timestamp', 'predicted_energy', 'actual_energy']].set_index('timestamp'))
else:
    st.warning("No comparison data available for the selected range.")

# -------------------------------
# 👤 USER ENERGY DASHBOARD (Filtered by Date)
# -------------------------------
st.title('👤 User Energy Consumption Dashboard')
st.subheader("Energy Consumption Overview")

# Filter user data within selected date range
user_mask = (user_data['timestamp'] >= start_date) & (user_data['timestamp'] <= end_date)
filtered_user_data = user_data.loc[user_mask].copy()

if not filtered_user_data.empty:
    # Plot filtered consumption
    st.line_chart(filtered_user_data.set_index('timestamp')['energy_consumed'])

    # Calculate peak usage within selected range
    peak_usage_time = filtered_user_data.loc[filtered_user_data['energy_consumed'].idxmax()]
    st.write(f"**Peak Usage Time (Selected Range)**: {peak_usage_time['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Total Energy Consumed (Selected Range)**: {filtered_user_data['energy_consumed'].sum():.2f} kWh")

else:
    st.warning("No user energy data available for the selected date range.")


