import streamlit as st
import pandas as pd
import SuggestionStorage as storage
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AeroSky Admin Panel",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 AeroSky Administrator Dashboard")

# -----------------------------
# LOGIN SYSTEM (simple)
# -----------------------------
ADMIN_PASSWORD = "AeroSky2026"   # change this later if needed

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.subheader("Login Required")

    password = st.text_input("Enter Admin Password", type="password")

    if st.button("Login"):

        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Incorrect password")

    st.stop()

# -----------------------------
# LOAD DATA
# -----------------------------
df = storage.get_suggestions()

st.success(f"Total suggestions: {len(df)}")

# -----------------------------
# SEARCH
# -----------------------------
st.subheader("🔍 Search Suggestions")

search = st.text_input("Search by operator name")

if search:
    df = df[df["Operator"].str.contains(search, case=False, na=False)]

# -----------------------------
# DISPLAY TABLE
# -----------------------------
st.subheader("📄 All Suggestions")

st.dataframe(df, use_container_width=True)

# -----------------------------
# DOWNLOAD CSV
# -----------------------------
csv_data = df.to_csv(index=False)

st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name="aerosky_suggestions.csv",
    mime="text/csv"
)

# -----------------------------
# DELETE SECTION
# -----------------------------
st.subheader("🗑 Delete Suggestion")

if len(df) > 0:

    suggestion_id = st.number_input(
        "Enter Suggestion ID to delete",
        min_value=1,
        step=1
    )

    if st.button("Delete"):

        storage.delete_suggestion(int(suggestion_id))
        st.warning(f"Suggestion {suggestion_id} deleted.")
        st.rerun()

# -----------------------------
# STATISTICS
# -----------------------------
st.subheader("📊 Statistics")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Suggestions", len(df))

with col2:
    if "Operator" in df.columns:
        st.metric("Unique Operators", df["Operator"].nunique())

# -----------------------------
# CHART (suggestions over time)
# -----------------------------
if not df.empty and "Timestamp" in df.columns:

    st.subheader("📈 Suggestions Over Time")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    chart_data = df.groupby(df["Timestamp"].dt.date).size()

    fig, ax = plt.subplots()
    chart_data.plot(kind="line", marker="o", ax=ax)

    ax.set_title("Suggestions Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Suggestions")

    st.pyplot(fig)