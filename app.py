import streamlit as st
import pandas as pd
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt

# Try importing local modules, but catch errors safely if they fail or hang
try:
    import SuggestionStorage as storage_mod
except Exception:
    storage_mod = None

try:
    from Weather import fetch_live_only_data
    from Indices import compute_all_indices
    BACKEND_AVAILABLE = True
except Exception:
    BACKEND_AVAILABLE = False

# ==========================================
# 1. GLOBAL PAGE CONFIGURATION & THEME INJECTION
# ==========================================
st.set_page_config(
    page_title="AeroSky Analytics — Kigali Station",
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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Fetch the global administrative override status
if storage_mod:
    global_use_mock = storage_mod.get_global_mock_status()
else:
    global_use_mock = not BACKEND_AVAILABLE

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Go to", ["Live Telemetry Dashboard", "Admin Login"])

if st.session_state.authenticated and st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.rerun()

# ==========================================
# 3. ADMIN PANEL VIEW (Controls Hidden Here Now)
# ==========================================
if app_mode == "Admin Login" or st.session_state.authenticated:
    if not st.session_state.authenticated:
        st.title("🔐 AeroSky Administrator Dashboard")
        st.subheader("Login Required")
        
        ADMIN_PASSWORD = "sylvere"  
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()
        
    st.title("🔐 AeroSky Administrator Dashboard")
    
    # MASTER SYSTEM CONTROLS — IMPACTS EVERYONE GLOBAL
    st.markdown("---")
    st.subheader("🛠️ Global Core Infrastructure Controls")
    
    if storage_mod:
        current_status = storage_mod.get_global_mock_status()
        admin_toggle = st.toggle("Force Safe Mock Data Framework globally (Bypasses API for ALL users)", value=current_status)
        
        if admin_toggle != current_status:
            storage_mod.set_global_mock_status(admin_toggle)
            st.toast(f"Global configuration modified! Mock Mode: {admin_toggle}", icon="⚙️")
            time.sleep(0.5)
            st.rerun()
    else:
        st.error("Infrastructure storage module missing. Cannot broadcast global switch.")

    if st.button("Clear App Calculation Cache Globally"):
        st.cache_data.clear()
        st.success("Application memory frames cleared completely.")
    
    st.markdown("---")
    
    if storage_mod:
        df_suggestions = storage_mod.get_suggestions()
    else:
        df_suggestions = pd.DataFrame(columns=["ID", "Operator", "Message", "Timestamp"])
        
    st.info(f"Total operator logs: {len(df_suggestions)}")

    st.subheader("🔍 Filter Log Registry")
    search = st.text_input("Search by operator designation")
    if search and not df_suggestions.empty:
        df_suggestions = df_suggestions[df_suggestions["Operator"].str.contains(search, case=False, na=False)]

    st.subheader("📄 Operational Suggestions Matrix")
    st.dataframe(df_suggestions, use_container_width=True)

    if not df_suggestions.empty:
        csv_data = df_suggestions.to_csv(index=False)
        st.download_button(label="📥 Download CSV Summary", data=csv_data, file_name="aerosky_suggestions.csv", mime="text/csv")

        st.subheader("🗑 Evict Registry Entry")
        suggestion_id = st.number_input("Enter Suggestion ID to delete", min_value=1, step=1)
        if st.button("Delete Entry") and storage_mod:
            storage_mod.delete_suggestion(int(suggestion_id))
            st.warning(f"Suggestion {suggestion_id} cleared.")
            time.sleep(1)
            st.rerun()

# ==========================================
# 4. MAIN TELEMETRY DASHBOARD VIEW
# ==========================================
else:
    def generate_fallback_mock_data():
        mock_df = pd.DataFrame([{
            'date': datetime.now(ZoneInfo("Africa/Kigali")).strftime('%Y-%m-%d'),
            'wind_speed_10m_max': 12.4,
            'precipitation_sum': 0.0,
            'visibility_mean': 11.2,
            'cloud_cover_mean': 18.0,
            'relative_humidity_2m_mean': 62.0,
            'temperature_2m_max': 27.5,
            'temperature_2m_min': 16.8,
            'surface_pressure_mean': 854.2,
            'sunrise': '06:04',
            'sunset': '18:15',
            'moon_phase': 'Waxing Gibbous',
            'ASI_Aviation': 94.5,
            'Aviation_Status': 'Optimal Conditions',
            'ASI_Astronomy': 88.0,
            'Astronomy_Status': 'Optimal Clear Skies'
        }])
        return mock_df

    # ------------------------------------------
    # FRAGMENT: Lightweight Independent Live Clock Header
    # ------------------------------------------
    @st.fragment(run_every=1.0)
    def run_live_clock_header():
        kigali_time = datetime.now(ZoneInfo("Africa/Kigali"))
        formatted_date = kigali_time.strftime('%A, %B %d, %Y')
        formatted_time = kigali_time.strftime('%H:%M:%S (GMT+2)')

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); padding:28px; border-radius:16px; margin-bottom:30px; color:white;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h1 style="margin:0; font-size:32px; font-weight:700; color:#FFFFFF;">AeroSky Analytics</h1>
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

    # 1. Render Clock Frame
    run_live_clock_header()

    # 2. Setup Layout Structural Elements
    telemetry_section = st.container()
    details_section = st.container()
    suggestion_section = st.container()

    # 3. Load Telemetry Data with Safety Measures
    with telemetry_section:
        st.markdown('<div class="section-header">📡 Real-Time Suitability Diagnostics</div>', unsafe_allow_html=True)
        
        today_row = None
        df = None

        # Evaluates the configuration specified by Admin panel
        if global_use_mock:
            df = generate_fallback_mock_data()
            today_row = df.iloc[-1]
            st.info("ℹ️ System currently operating on global Administrative Maintenance Mode (Safe Stream).")
        else:
            with st.status("Connecting to Live API Telemetry Stream...", expanded=False) as status:
                try:
                    raw_df = fetch_live_only_data()
                    df = compute_all_indices(raw_df)
                    today_row = df.iloc[-1]
                    status.update(label="Live telemetry engine connected successfully!", state="complete")
                except Exception as e:
                    status.update(label=f"External connection failed: {e}. Defaulting to backup matrix stream.", state="error")
                    df = generate_fallback_mock_data()
                    today_row = df.iloc[-1]

        # Render Metrics Grid
        if today_row is not None:
            diag_col1, diag_col2 = st.columns(2)
            
            av_status = today_row['Aviation_Status']
            av_class = "status-optimal" if "Optimal" in av_status else ("status-marginal" if "Marginal" in av_status else "status-suboptimal")
            as_status = today_row['Astronomy_Status']
            as_class = "status-optimal" if "Optimal" in as_status else ("status-marginal" if "Marginal" in as_status else "status-suboptimal")

            raw_vis = float(today_row.get('visibility_mean', 10000.0))
            vis_km = raw_vis / 1000.0 if raw_vis > 150.0 else raw_vis

            with diag_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <span style="font-size:14px; font-weight:600; color:#4B5563; text-transform:uppercase;">Flight Safety System</span>
                        <span class="status-badge {av_class}">{av_status}</span>
                    </div>
                    <h2 style="margin:0; font-size:36px; font-weight:700; color:#111827;">{float(today_row['ASI_Aviation']):.1f} <span style="font-size:16px; color:#6B7280;">/ 100 ASI</span></h2>
                    <div style="margin-top:14px; font-size:13px; color:#4B5563; border-top:1px solid #F3F4F6; padding-top:10px; display:flex; justify-content:space-between; gap:10px; flex-wrap:nowrap;">
                        <span style="white-space:nowrap;">💨 <b>Wind:</b> {float(today_row['wind_speed_10m_max']):.1f} km/h</span>
                        <span style="white-space:nowrap;">🌧️ <b>Rain:</b> {float(today_row['precipitation_sum']):.1f} mm</span>
                        <span style="white-space:nowrap;">👁️ <b>Range:</b> {vis_km:.1f} km</span>
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
                    <h2 style="margin:0; font-size:36px; font-weight:700; color:#111827;">{float(today_row['ASI_Astronomy']):.1f} <span style="font-size:16px; color:#6B7280;">/ 100 ASI</span></h2>
                    <div style="margin-top:14px; font-size:13px; color:#4B5563; border-top:1px solid #F3F4F6; padding-top:10px; display:flex; justify-content:space-between; gap:10px; flex-wrap:nowrap;">
                        <span style="white-space:nowrap;">☁️ <b>Clouds:</b> {float(today_row['cloud_cover_mean']):.1f}%</span>
                        <span style="white-space:nowrap;">🌖 <b>Moon:</b> {today_row['moon_phase']}</span>
                        <span style="white-space:nowrap;">💧 <b>Humidity:</b> {float(today_row['relative_humidity_2m_mean']):.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">🌤️ Live Kigali Environmental Conditions Matrix</div>', unsafe_allow_html=True)
            w_col1, w_col2, w_col3, w_col4, w_col5 = st.columns([1, 1, 1.2, 1, 1.2])
            
            with w_col1:
                st.metric(label="Temperature Profile", value=f"{float(today_row['temperature_2m_max']):.1f} °C", delta=f"Floor: {float(today_row['temperature_2m_min']):.1f} °C", delta_color="inverse")
            with w_col2:
                st.metric(label="Relative Air Humidity", value=f"{float(today_row['relative_humidity_2m_mean']):.1f}%")
            with w_col3:
                st.metric(label="Kigali QFE (KIA)", value=f"{float(today_row['surface_pressure_mean']):.1f} hPa")
            with w_col4:
                st.metric(label="Horizontal Visibility", value=f"{vis_km:.1f} km")
            with w_col5:
                st.metric(label="Solar Window Range", value=f"🌅 {today_row['sunrise']}", delta=f"🌇 Sunset: {today_row['sunset']}", delta_color="off")

            st.markdown('<div class="section-header">🔍 Current Frame Log Registry</div>', unsafe_allow_html=True)
            columns_to_show = [
                'date', 'ASI_Aviation', 'Aviation_Status', 'ASI_Astronomy', 'Astronomy_Status',
                'precipitation_sum', 'wind_speed_10m_max', 'cloud_cover_mean', 'relative_humidity_2m_mean', 'visibility_mean', 'moon_phase'
            ]
            
            df_display = df.copy()
            df_display['visibility_mean'] = df_display['visibility_mean'].apply(lambda x: x / 1000.0 if x > 150.0 else x)

            st.dataframe(
                df_display[columns_to_show], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "ASI_Aviation": st.column_config.NumberColumn(format="%.1f"),
                    "ASI_Astronomy": st.column_config.NumberColumn(format="%.1f"),
                    "precipitation_sum": st.column_config.NumberColumn(format="%.1f"),
                    "wind_speed_10m_max": st.column_config.NumberColumn(format="%.1f"),
                    "cloud_cover_mean": st.column_config.NumberColumn(format="%.1f"),
                    "relative_humidity_2m_mean": st.column_config.NumberColumn(format="%.1f"),
                    "visibility_mean": st.column_config.NumberColumn(label="visibility_mean (km)", format="%.1f")
                }
            )

    # ------------------------------------------
    # 4. CORE SYSTEM DETAILS & BACKEND LINKS
    # ------------------------------------------
    with details_section:
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

    # ------------------------------------------
    # 5. SYSTEM OPERATOR SUGGESTION BOX
    # ------------------------------------------
    with suggestion_section:
        st.markdown('<div class="section-header">📩 System Operator Suggestion Box</div>', unsafe_allow_html=True)
        with st.form("suggestion_box_stable_form", clear_on_submit=True):
            op_title = st.text_input("Operator Designation", placeholder="e.g., ATC, Dispatcher, astronomer, a student, etc")
            op_message = st.text_area("Suggestions for System Improvement", placeholder="Type your core system feedback or parameter changes here...")
            submitted = st.form_submit_button("Transmit your suggestion")
            
            if submitted and storage_mod:
                if op_message.strip():
                    success, response_msg = storage_mod.save_operator_suggestion(op_title, op_message)
                    if success:
                        st.toast("Feedback transmitted successfully!", icon="💾")
                        st.success(response_msg)
                    else:
                        st.error(response_msg)
                else:
                    st.warning("Please input message content before transmitting.")
            elif submitted:
                st.error("Suggestion storage link is offline.")

    # Base Page Footer
    st.markdown(
        "<hr><p style='text-align: center; color: #6B7280; font-size: 13px; font-weight: 500; letter-spacing: 0.025em;'>"
        "⚡ Designed & Built by <b>Sindambiwe Sylvere</b> | AeroSky Telemetry Core © 2026"
        "</p>", 
        unsafe_allow_html=True
    )
