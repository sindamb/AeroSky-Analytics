import streamlit as st
import pandas as pd
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt

# Import your local storage and backend modules
import SuggestionStorage as storage_mod
from Weather import fetch_live_only_data
from Indices import compute_all_indices

# ==========================================
# 1. GLOBAL PAGE CONFIGURATION & THEME INJECTION
# ==========================================
st.set_page_config(
    page_title="AeroSky Premium Analytics — Kigali Station",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
        html, body, [data-testid="stMarkdownContainer"] {
            font-family: 'Inter', sans-serif;
        }
        .metric-card {
            background: #ffffff;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            border: 1px solid #E5E7EB;
            margin-bottom: 15px;
        }
        .section-header {
            font-size: 20px;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 15px;
            margin-top: 15px;
        }
        .status-badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            display: inline-block;
        }
        .status-optimal { background-color: #DCFCE7; color: #166534; }
        .status-marginal { background-color: #FEF9C3; color: #854D0E; }
        .status-suboptimal { background-color: #FEE2E2; color: #991B1B; }
    </style>
""", unsafe_allow_html=True)

# Initialize Authentication State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ==========================================
# 2. SIDEBAR NAVIGATION & HIDDEN ACCESS
# ==========================================
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to", ["Live Telemetry Dashboard", "Admin Login"])

# Show a quick log-out option if already authenticated
if st.session_state.authenticated:
    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# 3. ADMIN PANEL VIEW
# ==========================================
if app_mode == "Admin Login" or st.session_state.authenticated:
    
    if not st.session_state.authenticated:
        st.title("🔐 AeroSky Administrator Dashboard")
        st.subheader("Login Required")
        
        ADMIN_PASSWORD = "AeroSky2026"  
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()
        
    # Content visible ONLY to you after login
    st.title("🔐 AeroSky Administrator Dashboard")
    df_suggestions = storage_mod.get_suggestions()
    st.success(f"Total suggestions: {len(df_suggestions)}")

    # Search
    st.subheader("🔍 Search Suggestions")
    search = st.text_input("Search by operator name")
    if search:
        df_suggestions = df_suggestions[df_suggestions["Operator"].str.contains(search, case=False, na=False)]

    # Display Data Table
    st.subheader("📄 All Suggestions")
    st.dataframe(df_suggestions, use_container_width=True)

    # Download CSV
    csv_data = df_suggestions.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="aerosky_suggestions.csv",
        mime="text/csv"
    )

    # Delete Section
    st.subheader("🗑 Delete Suggestion")
    if len(df_suggestions) > 0:
        suggestion_id = st.number_input("Enter Suggestion ID to delete", min_value=1, step=1)
        if st.button("Delete"):
            storage_mod.delete_suggestion(int(suggestion_id))
            st.warning(f"Suggestion {suggestion_id} deleted.")
            time.sleep(1) # Give time for user to see message
            st.rerun()

    # Statistics & Trends Charts
    st.subheader("📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Suggestions", len(df_suggestions))
    with col2:
        if "Operator" in df_suggestions.columns:
            st.metric("Unique Operators", df_suggestions["Operator"].nunique())

    if not df_suggestions.empty and "Timestamp" in df_suggestions.columns:
        st.subheader("📈 Suggestions Over Time")
        df_suggestions["Timestamp"] = pd.to_datetime(df_suggestions["Timestamp"], errors="coerce")
        chart_data = df_suggestions.groupby(df_suggestions["Timestamp"].dt.date).size()

        fig, ax = plt.subplots()
        chart_data.plot(kind="line", marker="o", ax=ax)
        ax.set_title("Suggestions Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Suggestions")
        st.pyplot(fig)


# ==========================================
# 4. MAIN TELEMETRY DASHBOARD VIEW
# ==========================================
else:
    # Setup placeholders for the live dashboard
    header_placeholder = st.empty()
    diagnostic_container = st.container()
    matrix_container = st.container()
    table_placeholder = st.empty()

    details_and_links_container = st.container()
    suggestion_box_container = st.container()
    developer_footer_placeholder = st.empty()

    @st.cache_data(ttl=60)
    def fetch_and_calculate_live_metrics():
        raw_df = fetch_live_only_data()
        return compute_all_indices(raw_df)

    # Isolated Live Auto-refresh fragment
    @st.fragment
    def run_live_telemetry_loop():
        kigali_time = datetime.now(ZoneInfo("Africa/Kigali"))
        formatted_date = kigali_time.strftime('%A, %B %d, %Y')
        formatted_time = kigali_time.strftime('%H:%M:%S (GMT+2)')

        header_placeholder.markdown(f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); padding:28px; border-radius:16px; margin-bottom:30px; color:white;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h1 style="margin:0; font-size:32px; font-weight:700; color:#FFFFFF;">AeroSky Live Station Tracker</h1>
                        <span style="background: rgba(255, 255, 255, 0.15); font-size: 11px; padding: 4px 8px; border-radius: 4px; font-weight: 600;">KGL</span>
                    </div>
                    <p style="margin:4px 0 0 0; font-size:14px; color:#93C5FD;">📍 Station: <b>Kigali, Rwanda</b></p>
                </div>
                <div style="display:flex; gap:12px; align-items:center;">
                    <span style="background: rgba(255,255,255,0.1); padding:8px 14px; border-radius:8px; font-size:14px;">📅 {formatted_date}</span>
                    <span style="background: #2563EB; padding:8px 14px; border-radius:8px; font-size:14px; font-weight:700; font-family: monospace;">🕒 {formatted_time}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if "loop_counter" not in st.session_state:
            st.session_state.loop_counter = 0
        st.session_state.loop_counter += 1
        if st.session_state.loop_counter >= 60:
            st.session_state.loop_counter = 0
            st.cache_data.clear()

        try:
            df = fetch_and_calculate_live_metrics()
            today_row = df.iloc[-1]
        except Exception as e:
            st.error(f"Data engine offline: {e}")
            return

        with diagnostic_container:
            st.markdown('<div class="section-header">📡 Real-Time Suitability Diagnostics</div>', unsafe_allow_html=True)
            diag_col1, diag_col2 = st.columns(2)
            
            av_status = today_row['Aviation_Status']
            av_class = "status-optimal" if "Optimal" in av_status else ("status-marginal" if "Marginal" in av_status else "status-suboptimal")
            as_status = today_row['Astronomy_Status']
            as_class = "status-optimal" if "Optimal" in as_status else ("status-marginal" if "Marginal" in as_status else "status-suboptimal")

            with diag_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:14px; font-weight:600; color:#4B5563; text-transform:uppercase;">Flight Safety System</span>
                        <span class="status-badge {av_class}">{av_status}</span>
                    </div>
                    <h2 style="margin:0; font-size:36px; font-weight:700; color:#111827;">{today_row['ASI_Aviation']:.1f} <span style="font-size:16px; color:#6B7280;">/ 100 ASI</span></h2>
                    <div style="margin-top:14px; font-size:13px; color:#4B5563; border-top:1px solid #F3F4F6; padding-top:10px; display:flex; gap:15px;">
                        <span>💨 <b>Wind:</b> {today_row['wind_speed_10m_max']} km/h</span>
                        <span>🌧️ <b>Rain:</b> {today_row['precipitation_sum']} mm</span>
                        <span>👁️ <b>Range:</b> {today_row['visibility_mean']/1000.0:.1f} km</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with diag_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:14px; font-weight:600; color:#4B5563; text-transform:uppercase;">Observation Window</span>
                        <span class="status-badge {as_class}">{as_status}</span>
                    </div>
                    <h2 style="margin:0; font-size:36px; font-weight:700; color:#111827;">{today_row['ASI_Astronomy']:.1f} <span style="font-size:16px; color:#6B7280;">/ 100 ASI</span></h2>
                    <div style="margin-top:14px; font-size:13px; color:#4B5563; border-top:1px solid #F3F4F6; padding-top:10px; display:flex; gap:12px; justify-content:space-between;">
                        <span>☁️ <b>Clouds:</b> {today_row['cloud_cover_mean']}%</span>
                        <span>🌖 <b>Moon:</b> {today_row['moon_phase']}</span>
                        <span>💧 <b>Humidity:</b> {today_row['relative_humidity_2m_mean']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with matrix_container:
            st.markdown('<div class="section-header">🌤️ Live Kigali Environmental Conditions Matrix</div>', unsafe_allow_html=True)
            w_col1, w_col2, w_col3, w_col4, w_col5 = st.columns(5)
            with w_col1:
                st.metric(label="Temperature Profile", value=f"{today_row['temperature_2m_max']} °C", delta=f"Floor: {today_row['temperature_2m_min']} °C", delta_color="inverse")
            with w_col2:
                st.metric(label="Relative Air Humidity", value=f"{today_row['relative_humidity_2m_mean']}%")
            with w_col3:
                st.metric(label="Kigali QFE (KIA) ", value=f"{today_row['surface_pressure_mean']:.1f} hPa")
            with w_col4:
                vis_km = today_row['visibility_mean'] / 1000.0 if today_row['visibility_mean'] > 100 else today_row['visibility_mean']
                st.metric(label="Horizontal Visibility", value=f"{vis_km:.1f} km")
            with w_col5:
                st.metric(label="Solar Window Range", value=f"🌅 {today_row['sunrise']}", delta=f"🌇 Sunset: {today_row['sunset']}", delta_color="off")

        with table_placeholder:
            st.markdown('<div class="section-header">🔍 Current Frame Log Registry</div>', unsafe_allow_html=True)
            columns_to_show = [
                'date', 'ASI_Aviation', 'Aviation_Status', 'ASI_Astronomy', 'Astronomy_Status',
                'precipitation_sum', 'wind_speed_10m_max', 'cloud_cover_mean', 'relative_humidity_2m_mean', 'visibility_mean', 'moon_phase'
            ]
            st.dataframe(df[columns_to_show], width='stretch', hide_index=True)

        time.sleep(1)
        st.rerun()

    # Static elements stay rock solid here outside the fragment's loop scope
    with details_and_links_container:
        st.markdown("---")
        st.markdown('<div class="section-header">📘 AeroSky Core System Details</div>', unsafe_allow_html=True)
        with st.expander("Explore Index Calculations, Formulas, & Operational Network Links", expanded=True):
            st.markdown("""
            The **Atmospheric Suitability Index (ASI)** metrics assess live telemetry streams to verify flight dispatcher safety envelopes and optical deep-sky conditions for astronomical observations.
            
            #### External Operational Connections
            * 🌐 **Data Feed Engine**: Powered by the [Open-Meteo Weather API](https://open-meteo.com)
            * ✈️ **Primary Airport Hub**: [Kigali International Airport (HRYR) Portal](https://www.rac.co.rw)
            * 🌌 **Astronomy Network**: Developed alongside the [Inzagi Astro Group (IAG)](https://inzagi-astrogroup.vercel.app/)
            """)

    with suggestion_box_container:
        st.markdown('<div class="section-header">📩 System Operator Suggestion Box</div>', unsafe_allow_html=True)
        with st.form("suggestion_box_stable_form", clear_on_submit=True):
            op_title = st.text_input("Operator Designation", placeholder="e.g., ATC, Dispatcher, astronomer, a student, etc")
            op_message = st.text_area("Suggestions for System Improvement", placeholder="Type your core system feedback or parameter changes here...")
            submitted = st.form_submit_button("Transmit your suggestion")
            
            if submitted:
                if op_message.strip():
                    success, response_msg = storage_mod.save_operator_suggestion(op_title, op_message)
                    if success:
                        st.toast("Feedback transmitted successfully!", icon="💾")
                        st.success(response_msg)
                    else:
                        st.error(response_msg)
                else:
                    st.warning("Please input message content before transmitting.")

    developer_footer_placeholder.markdown(
        "<hr><p style='text-align: center; color: #6B7280; font-size: 13px; font-weight: 500; letter-spacing: 0.025em;'>"
        "⚡ Designed & Built by <b>Sindambiwe Sylvere</b> | AeroSky Telemetry Core © 2026"
        "</p>", 
        unsafe_allow_html=True
    )

    # Start the ticking logic safely at the layout floor
    run_live_telemetry_loop()