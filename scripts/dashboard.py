import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import plotly.express as px

# ==========================
# Load biến môi trường
# ==========================
load_dotenv()
print(os.getenv("DATABASE_URL"))

try:
    engine = create_engine(os.getenv("DATABASE_URL_DASHBOARD"))
except Exception as e:
    st.error(f"Error connecting to database: {e}")

# ==========================
# Tiêu đề dashboard
# ==========================
st.title("🌤️ Weather Dashboard")

# ==========================
# Sidebar: Bộ lọc
# ==========================
st.sidebar.header("Filter Options")
cities = st.sidebar.multiselect(
    "Select Cities",
    options=["Hanoi", "Ho Chi Minh City", "Da Nang", "Hai Phong", "Can Tho", "Nha Trang"],
    default=["Hanoi", "Ho Chi Minh City"]
)
date_range = st.sidebar.date_input("Select Date Range", [])

# ==========================
# Truy vấn dữ liệu
# ==========================
query = "SELECT * FROM weather_data"
conditions = []

if cities:
    conditions.append(f"city IN {tuple(cities)}")
if date_range and len(date_range) == 2:
    conditions.append(f"timestamp BETWEEN '{date_range[0]}' AND '{date_range[1]}'")

if conditions:
    query += " WHERE " + " AND ".join(conditions)

st.write("📜 Query:", query)

try:
    df = pd.read_sql(query, engine)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    df = pd.DataFrame()

# ==========================
# Hiển thị dữ liệu có phân trang
# ==========================
if not df.empty:
    st.subheader("Weather Data")

    # --- Số dòng mỗi trang ---
    rows_per_page = st.sidebar.slider("Rows per page", 5, 50, 10)

    # --- Khởi tạo session_state ---
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    # --- Tổng số trang ---
    total_pages = (len(df) - 1) // rows_per_page + 1

    # --- Điều hướng ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Prev") and st.session_state.page_number > 0:
            st.session_state.page_number -= 1
    with col3:
        if st.button("Next ➡️") and st.session_state.page_number < total_pages - 1:
            st.session_state.page_number += 1

    # --- Thông tin trang ---
    with col2:
        st.markdown(
            f"<div style='text-align:center;'>Page {st.session_state.page_number + 1} of {total_pages}</div>",
            unsafe_allow_html=True
        )

    # --- Cắt dữ liệu hiển thị ---
    start_idx = st.session_state.page_number * rows_per_page
    end_idx = start_idx + rows_per_page
    page_data = df.iloc[start_idx:end_idx]

    # --- Hiển thị bảng ---
    st.dataframe(page_data[['city', 'temp', 'humidity', 'weather_description', 'timestamp']])

    # ==========================
    # Biểu đồ
    # ==========================
    st.subheader("Temperature Trend")
    fig = px.line(
        df,
        x="timestamp",
        y="temp",
        color="city",
        title="Temperature Over Time",
        labels={"temp": "Temperature (°C)", "timestamp": "Time"}
    )
    st.plotly_chart(fig)

    st.subheader("Humidity Trend")
    fig_humidity = px.line(
        df,
        x="timestamp",
        y="humidity",
        color="city",
        title="Humidity Over Time",
        labels={"humidity": "Humidity (%)", "timestamp": "Time"}
    )
    st.plotly_chart(fig_humidity)

else:
    st.warning("⚠️ No data available for the selected filters.")
