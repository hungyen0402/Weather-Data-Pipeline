import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import plotly.express as px

# ==========================
# Load biến môi trường
# ==========================
load_dotenv()
print(os.getenv("DATABASE_URL_RAILWAY"))

# Tạo engine kết nối database
try:
    engine = create_engine(os.getenv("DATABASE_URL_RAILWAY"))
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
# Tạo truy vấn SQL an toàn
# ==========================
base_query = "SELECT * FROM weather_data"
conditions = []
params = {}

# ---- Lọc theo city ----
if cities:
    if len(cities) == 1:
        conditions.append("city = :city")
        params["city"] = cities[0]
    else:
        city_placeholders = []
        for i, city in enumerate(cities):
            key = f"city_{i}"
            city_placeholders.append(f":{key}")
            params[key] = city
        conditions.append(f"city IN ({', '.join(city_placeholders)})")

# ---- Lọc theo ngày ----
if date_range and len(date_range) == 2:
    conditions.append("timestamp BETWEEN :start_date AND :end_date")
    params["start_date"] = f"{date_range[0]} 00:00:00"
    params["end_date"] = f"{date_range[1]} 23:59:59"
elif date_range and len(date_range) == 1:
    conditions.append("timestamp BETWEEN :start_date AND :end_date")
    params["start_date"] = f"{date_range[0]} 00:00:00"
    params["end_date"] = f"{date_range[0]} 23:59:59"

# ---- Gộp điều kiện ----
if conditions:
    base_query += " WHERE " + " AND ".join(conditions)

# In query (debug)
st.write("📜 Query:", base_query)
st.write("🔧 Params:", params)

# ==========================
# Lấy dữ liệu
# ==========================
try:
    with engine.connect() as conn:
        df = pd.read_sql(text(base_query), conn, params=params)
except Exception as e:
    st.error(f"Error fetching data: {e}")
    df = pd.DataFrame()
#=========================
# HÀM CONVERT FOR DOWNLOAD 
@st.cache_data
def convert_for_download(dff):
    return dff.to_csv().encode("utf-8")
# ==========================
# Hiển thị dữ liệu có phân trang
# ==========================
if not df.empty:
    st.subheader("Weather Data")

    #==============================
    # --- Button Download -------
    #==============================
    csv = convert_for_download(df)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv,
        file_name="data_weather.csv",
        mime="text/csv",
        icon=":material/download:"
    )
    # --- Nút sắp xếp ---
    reverse_order = st.sidebar.checkbox("Sort newest first (descending)", value=True)
    if reverse_order:
        df = df.sort_values(by="timestamp", ascending=False).reset_index(drop=True)
    else:
        df = df.sort_values(by="timestamp", ascending=True).reset_index(drop=True)

    # --- Số dòng mỗi trang ---
    rows_per_page = st.sidebar.slider("Rows per page", 5, 50, 10)

    # --- Khởi tạo session_state ---
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    # --- Tổng số trang ---
    total_pages = (len(df) - 1) // rows_per_page + 1

    # --- Chọn trang cụ thể ---
    page_input = st.sidebar.number_input(
        "Go to page:", min_value=1, max_value=total_pages, value=st.session_state.page_number + 1
    )
    st.session_state.page_number = page_input - 1

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
    if date_range:
        if len(date_range) == 2:
            st.subheader(f"Temperature Trend ({date_range[0]} → {date_range[1]})")
        if len(date_range) == 1:
            st.subheader(f"Temperature Trend ({date_range[0]})")
    else:
        st.subheader("Temperature Trend")

    fig_temp = px.line(
        df,
        x="timestamp",
        y="temp",
        color="city",
        title="Temperature Over Time",
        labels={"temp": "Temperature (°C)", "timestamp": "Time"}
    )
    st.plotly_chart(fig_temp)

    if date_range:
        if len(date_range) == 2:
            st.subheader(f"Humidity Trend ({date_range[0]} → {date_range[1]})")
        if len(date_range) == 1:
            st.subheader(f"Humidity Trend ({date_range[0]})")
    else:
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
