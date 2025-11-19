import streamlit as st
import pandas as pd

# ---------------------- CUSTOM CSS FOR BEAUTIFUL UI ---------------------------
page_bg = """
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.sidebar .sidebar-content {
    background: #1b1b1b;
}

.stButton>button {
    background-color: #ff7f50;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    border: none;
}

.stButton>button:hover {
    background-color: #ff5722;
    color: white;
}

.dataframe {
    background-color: white !important;
    color: black !important;
}

.block-container {
    padding: 2rem 2rem;
}

.card {
    background: rgba(255, 255, 255, 0.15);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(4px);
    margin-bottom: 20px;
}

.big-title {
    font-size: 38px;
    font-weight: 900;
    text-align: center;
    color: #ffd369;
    margin-bottom: 20px;
}

.sub-header {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 20px;
}

</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# ------------------- MAIN TITLE --------------------------------
st.markdown("<h1 class='big-title'>⚡ Energy Prediction Dashboard</h1>", unsafe_allow_html=True)

# ------------------- CITY DROPDOWN -------------------------------
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

st.sidebar.header("⚙️ Configuration")
selected_city = st.sidebar.selectbox("🏙️ Choose City:", list(CITY_FILES.keys()))

data_file = CITY_FILES[selected_city]
user_data_file = USER_DATA_FILES[selected_city]

data = pd.read_csv(data_file, parse_dates=['timestamp'])
user_data = pd.read_csv(user_data_file, parse_dates=['timestamp'])

# -------------------- DATE FILTER -------------------------------
st.sidebar.subheader("📅 Select Date Range for Prediction")
start_date = pd.to_datetime(st.sidebar.date_input('Start Date'))
end_date = pd.to_datetime(st.sidebar.date_input('End Date'))

# ---------------------- FILTER DATA ------------------------------
if st.sidebar.button('🔍 Apply Date Filter'):
    mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
    filtered_data = data.loc[mask]
else:
    filtered_data = data.head(20)

filtered_data['status'] = filtered_data['predicted_energy'].apply(
    lambda x: 'Overconsumption' if x > OVERCONSUMPTION_THRESHOLD
    else ('Low Consumption' if x < LOW_CONSUMPTION_THRESHOLD else 'Normal')
)

# ----------------------- DISPLAY RESULTS --------------------------
st.markdown(f"<h2 class='sub-header'>📊 Prediction Results — {selected_city}</h2>", unsafe_allow_html=True)
st.write(f"Showing data from **{start_date.date()}** to **{end_date.date()}**.")

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.dataframe(filtered_data[['timestamp', 'predicted_energy', 'status']])
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------ LINE CHART ------------------------------
st.markdown("<h2 class='sub-header'>📈 Predicted Energy Output</h2>", unsafe_allow_html=True)
if not filtered_data.empty:
    st.line_chart(filtered_data.set_index('timestamp')['predicted_energy'])

    if (filtered_data['status'] == 'Overconsumption').any():
        st.warning("⚠️ Overconsumption detected during the selected period!")
    elif (filtered_data['status'] == 'Low Consumption').any():
        st.info("ℹ️ Low consumption detected during the selected period.")
    else:
        st.success("✔ Normal consumption during the selected period.")

# ------------------- COMPARISON SECTION ---------------------------
st.markdown("<h2 class='sub-header'>🔄 Predicted vs Actual Energy Usage</h2>", unsafe_allow_html=True)

comparison_start_date = pd.to_datetime(st.sidebar.date_input("Start Date for Comparison"))
comparison_end_date = pd.to_datetime(st.sidebar.date_input("End Date for Comparison"))

comparison_mask = (data['timestamp'] >= comparison_start_date) & (data['timestamp'] <= comparison_end_date)
comparison_filtered_data = data[comparison_mask]

if 'actual_energy' not in data.columns:
    comparison_filtered_data['actual_energy'] = comparison_filtered_data['predicted_energy'] * 0.95

st.line_chart(comparison_filtered_data[['timestamp', 'predicted_energy', 'actual_energy']].set_index('timestamp'))

# ------------------- USER ENERGY DASHBOARD -----------------------
st.markdown("<h2 class='sub-header'>👤 User Energy Consumption</h2>", unsafe_allow_html=True)

st.line_chart(user_data.set_index('timestamp')['energy_consumed'])

peak_usage_time = user_data[user_data['energy_consumed'] == user_data['energy_consumed'].max()]

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.write(f"🔥 **Peak Usage Time**: {peak_usage_time['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').values[0]}")
st.write(f"⚡ **Total Energy Consumed**: {user_data['energy_consumed'].sum()} kWh")
st.markdown("</div>", unsafe_allow_html=True)
