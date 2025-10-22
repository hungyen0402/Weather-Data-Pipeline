import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
import io # Cần thiết để hiển thị output của df.info()

# Import thư viện biểu đồ
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud

# ==========================================
# CÀI ĐẶT TRANG (Nên đặt ở đầu)
# ==========================================
st.set_page_config(
    page_title="Phân Tích Sâu Dữ Liệu Thời Tiết",
    layout="wide" # Sử dụng toàn bộ chiều ngang
)

# ==========================================
# HÀM TẢI DỮ LIỆU (Cache để tăng tốc)
# ==========================================
@st.cache_data
def load_data():
    """
    Kết nối và tải dữ liệu CHỈ CỦA HANOI VÀ HAI PHONG
    từ database Postgres trên Railway.
    """
    try:
        # Lấy URL database từ biến môi trường của Railway
        db_url = os.environ.get("DATABASE_URL")
        if db_url is None:
            st.error("Không tìm thấy DATABASE_URL. Bạn đã thêm biến môi trường chưa?")
            return pd.DataFrame()

        engine = create_engine(db_url)
        
        # --- YÊU CẦU CỦA BẠN: Chỉ truy vấn Hanoi và Hai Phong ---
        query = text("SELECT * FROM weather_data WHERE city IN (:city1, :city2)")
        df = pd.read_sql(query, engine, params={"city1": "Hanoi", "city2": "Hai Phong"})
        
        # --- Bắt đầu phần Data Processing từ Notebook ---
        
        # 1. Xử lý thiếu (Dù hiện tại không có, đây là good practice)
        df['temp'] = df['temp'].fillna(df['temp'].mean())
        df['humidity'] = df['humidity'].fillna(df['humidity'].mean())

        # 2. Chuẩn hóa kiểu dữ liệu
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['temp'] = df['temp'].astype(float)
        df['temp_min'] = df['temp_min'].astype(float)
        df['temp_max'] = df['temp_max'].astype(float)
        df['humidity'] = df['humidity'].astype(int)
        df['pressure'] = df['pressure'].astype(int)
        df['wind_speed'] = df['wind_speed'].astype(float)
        df['wind_deg'] = df['wind_deg'].astype(int)
        df['visibility'] = df['visibility'].astype(int)

        # 3. Tạo cột đặc trưng mới
        df['temp_diff'] = df['temp_max'] - df['temp_min']
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek

        def wind_dir_category(deg):
            if deg < 45 or deg >= 315: return 'North'
            elif 45 <= deg < 135: return 'East'
            elif 135 <= deg < 225: return 'South'
            else: return 'West'
        
        df['wind_direction_category'] = df['wind_deg'].apply(wind_dir_category)
        df['is_clear_sky'] = (df['weather_description'] == 'clear sky').astype(int)
        
        return df

    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu: {e}")
        return pd.DataFrame()

# Tải dữ liệu
df = load_data()

if df.empty:
    st.warning("Không thể tải dữ liệu. Vui lòng kiểm tra lại kết nối database.")
else:
    # ==========================================
    # BẮT ĐẦU NỘI DUNG TỪ NOTEBOOK
    # ==========================================

    # --- Phần 1: Deploy và Preprocessing (Giới thiệu) ---
    st.title("Phần 1: Chuẩn hóa và Xử lý dữ liệu")
    # Thay thế ảnh chụp màn hình cục bộ bằng ảnh bạn đã tải lên (image_297441.png)
    # **Lưu ý**: Bạn cần thêm ảnh này vào repository (ví dụ: trong thư mục `images/`) 
    # và đổi đường dẫn ở dưới nếu cần.
    try:
        # Giả sử bạn tạo thư mục 'images' và lưu ảnh vào đó
        st.image("image_297441.png", caption="Ảnh chụp hệ thống Dashboard đã deploy", width=800)
    except Exception as e:
        st.warning(f"Không tìm thấy file ảnh 'image_297441.png'. Lỗi: {e}")

    st.header("Đọc dữ liệu từ Database (Chỉ Hà Nội & Hải Phòng)")
    
    st.subheader("Dữ liệu ban đầu (Head 10):")
    st.dataframe(df.head(10))

    st.subheader("Thông tin dữ liệu (Data Info):")
    # Bắt output của df.info() để hiển thị trong Streamlit
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)

    st.header("Data Preprocessing & Feature Engineering")
    st.markdown("Dữ liệu đã được xử lý thiếu, chuẩn hóa kiểu dữ liệu và tạo thêm các cột đặc trưng mới để phân tích.")
    st.subheader("Dữ liệu sau khi tạo cột mới (Head 10):")
    st.dataframe(df.head(10))

    # --- Phần 2: Biểu diễn dữ liệu ---
    st.title("Phần 2: Biểu diễn dữ liệu (Hà Nội & Hải Phòng)")

    # 1. Histogram
    st.header("2. Histogram: Phân phối nhiệt độ")
    st.markdown("👉 **Nhận xét:** Các thành phố lớn ở Miền Bắc có biên độ nhiệt độ lớn trong khoảng thời gian rất ngắn. Chỉ trong 4 ngày (18/10 - 21/10/2025), nhiệt độ trải dài từ 22°C tới hơn 32°C.")
    fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
    ax_hist.hist(df[df['city'] == 'Hanoi']['temp'], bins=30, alpha=0.6, label='Hanoi', color='orange', edgecolor='black')
    ax_hist.hist(df[df['city'] == 'Hai Phong']['temp'], bins=30, alpha=0.6, label='Hai Phong', color='skyblue', edgecolor='black')
    ax_hist.set_title('Phân phối nhiệt độ: Hà Nội vs Hải Phòng')
    ax_hist.set_xlabel('Nhiệt độ (°C)')
    ax_hist.set_ylabel('Số lượng')
    ax_hist.legend()
    st.pyplot(fig_hist)

    # 2. Boxplot
    st.header("3. Boxplot: So sánh nhiệt độ")
    st.markdown("👉 **Nhận xét:** Sự chênh lệch nhiệt độ giữa Hải Phòng (ven biển) và Hà Nội (lục địa) không quá lớn, cho thấy sự phân bố nhiệt độ ở Miền Bắc khá đồng đều.")
    fig_box, ax_box = plt.subplots(figsize=(10, 6))
    # Lọc dữ liệu để đảm bảo boxplot chỉ vẽ 2 thành phố này
    data_to_plot = [df[df['city'] == 'Hanoi']['temp'].dropna(), df[df['city'] == 'Hai Phong']['temp'].dropna()]
    ax_box.boxplot(data_to_plot, labels=['Hanoi', 'Hai Phong'])
    ax_box.set_title('Phân bố nhiệt độ theo thành phố')
    ax_box.set_xlabel('Thành phố')
    ax_box.set_ylabel('Nhiệt độ (°C)')
    st.pyplot(fig_box)

    # 3. Line Plot (Nhiệt độ)
    st.header("4. Line Plot: Xu hướng nhiệt độ")
    st.markdown("👉 **Nhận xét:** Hiện tượng giảm nhiệt độ đột ngột. Trong 2 ngày 20 và 21/10, nhiệt độ trung bình từ 32°C giảm sâu xuống 26°C, có thời điểm (ban đêm) xuống còn 22-24°C.")
    # Sử dụng Plotly Express để dễ dàng nhóm theo thành phố
    df_grouped_temp = df.groupby(['timestamp', 'city'])['temp'].mean().reset_index()
    fig_line_temp = px.line(df_grouped_temp, x='timestamp', y='temp', color='city',
                            title='Xu hướng nhiệt độ theo thời gian (Hà Nội vs Hải Phòng)',
                            labels={'temp': 'Nhiệt độ (°C)', 'timestamp': 'Thời gian'})
    st.plotly_chart(fig_line_temp, use_container_width=True)


    # 4. Area Plot (Độ ẩm)
    st.header("5. Area Plot: Xu hướng độ ẩm")
    st.markdown("👉 **Nhận xét:** Độ ẩm trong khoảng thời gian này dao động trong khoảng 60%.")
    df_grouped_humidity = df.groupby(['timestamp', 'city'])['humidity'].mean().reset_index()
    fig_area_hum = px.area(df_grouped_humidity, x='timestamp', y='humidity', color='city',
                           title='Xu hướng độ ẩm theo thời gian (Hà Nội vs Hải Phòng)',
                           labels={'humidity': 'Độ ẩm (%)', 'timestamp': 'Thời gian'})
    st.plotly_chart(fig_area_hum, use_container_width=True)
    
    # 4.b Area Plot (Tốc độ gió - Thêm từ notebook)
    st.header("6. Area Plot: Xu hướng tốc độ gió")
    df_grouped_wind = df.groupby(['timestamp', 'city'])['wind_speed'].mean().reset_index()
    fig_area_wind = px.area(df_grouped_wind, x='timestamp', y='wind_speed', color='city',
                            title='Xu hướng tốc độ gió theo thời gian (Hà Nội vs Hải Phòng)',
                            labels={'wind_speed': 'Tốc độ (m/s)', 'timestamp': 'Thời gian'})
    st.plotly_chart(fig_area_wind, use_container_width=True)


    # 5. Scatter Plot (Plotly)
    st.header("7. Scatter Plot: Nhiệt độ vs Độ ẩm (Tương tác)")
    fig_scatter = px.scatter(df, x='temp', y='humidity', color='city', trendline="ols",
                             title='Mối quan hệ giữa nhiệt độ và độ ẩm (Hà Nội vs Hải Phòng)',
                             width=1000, height=500)
    fig_scatter.update_layout(xaxis_title='Nhiệt độ (°C)', yaxis_title='Độ ẩm (%)')
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 6. Heatmap
    st.header("8. Heatmap tương quan")
    # Lọc các cột số để tính toán tương quan
    numeric_cols = ['temp', 'temp_min', 'temp_max', 'humidity', 'pressure', 'wind_speed', 'wind_deg', 'visibility']
    correlation_matrix = df[numeric_cols].corr()
    fig_heatmap, ax_heatmap = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax_heatmap)
    ax_heatmap.set_title('Heatmap tương quan giữa các biến (Hà Nội & Hải Phòng)')
    st.pyplot(fig_heatmap)

    # 7. Treemap (Plotly)
    st.header("9. Treemap: Phân bố thời tiết (Tương tác)")
    fig_treemap = px.treemap(df, path=['city', 'weather_description'], values='temp',
                             title='Phân bố nhiệt độ theo thành phố và mô tả thời tiết (Hà Nội vs Hải Phòng)',
                             color='temp', color_continuous_scale='RdBu')
    st.plotly_chart(fig_treemap, use_container_width=True)

    # 8. WordCloud
    st.header("10. WordCloud: Mô tả thời tiết")
    text = ' '.join(df['weather_description'].dropna())
    if text:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig_wordcloud, ax_wordcloud = plt.subplots(figsize=(10, 5))
        ax_wordcloud.imshow(wordcloud, interpolation='bilinear')
        ax_wordcloud.set_title('WordCloud mô tả thời tiết (Hà Nội & Hải Phòng)')
        ax_wordcloud.axis('off')
        st.pyplot(fig_wordcloud)
    else:
        st.warning("Không có dữ liệu 'weather_description' để tạo WordCloud.")

    # 9. Sunburst (Plotly)
    st.header("11. Sunburst: Phân bố thời tiết (Tương tác)")
    fig_sunburst = px.sunburst(df, path=['city', 'weather_description'], values='temp',
                               title='Phân bố nhiệt độ theo thành phố và mô tả thời tiết (Hà Nội vs Hải Phòng)',
                               color='temp', color_continuous_scale='RdBu')
    st.plotly_chart(fig_sunburst, use_container_width=True)


    # --- Phần 3: Storytelling ---
    st.title("Phần 3: Hiện tượng chuyển mùa tại Miền Bắc (18-21/10/2025)")
    
    st.header("1. Sự giảm mạnh nhiệt độ: Dấu hiệu rõ nét của không khí lạnh")
    st.markdown("""
    Dữ liệu từ ngày 18/10 đến 21/10/2025 cho thấy nhiệt độ tại Hà Nội và Hải Phòng giảm đáng kể, từ mức cao của mùa hè (khoảng 31-32°C) xuống mức mát mẻ hơn (khoảng 23-24°C). Điều này phản ánh sự xâm nhập của khối không khí lạnh từ phương Bắc, thường gọi là "đợt rét đầu mùa" ở miền Bắc Việt Nam.

    **Phân tích từ biểu đồ Line Plot (Nhiệt độ theo thời gian):** Biểu đồ đường cho thấy đường cong nhiệt độ giảm dần theo timestamp. Tại Hà Nội, nhiệt độ bắt đầu ở mức 32.97°C vào chiều ngày 18/10 và giảm mạnh xuống còn 23.97-24.98°C vào ngày 21/10. Tương tự, tại Hải Phòng, nhiệt độ từ 31.97°C giảm xuống 22.97-23.97°C. Sự giảm này xảy ra đột ngột trong khoảng 3-4 ngày, với mức giảm trung bình 8-10°C, phù hợp với đặc trưng của gió mùa Đông Bắc khiến thời tiết chuyển từ nóng ẩm sang se lạnh.

    **Phân tích từ biểu đồ Boxplot (Nhiệt độ theo thành phố):** Boxplot nhấn mạnh sự biến động nhiệt độ giữa hai thành phố. Tại Hà Nội, median temp khoảng 31-32°C ở đầu dữ liệu, nhưng giảm xuống dưới 25°C ở cuối, với các outliers thấp hơn cho thấy những thời điểm lạnh đột ngột. Hải Phòng cũng tương tự, nhưng có độ biến thiên lớn hơn (whiskers rộng), phản ánh ảnh hưởng của gió biển làm nhiệt độ giảm nhanh hơn.

    **Phân tích từ biểu đồ Histogram (Phân bố nhiệt độ):** Histogram cho thấy phân bố nhiệt độ lệch phải ở đầu tháng (tập trung quanh 30-32°C, thời tiết hè), nhưng dần dịch chuyển sang trái về cuối tháng (tập trung quanh 23-25°C). Điều này chứng tỏ sự chuyển dịch toàn bộ phân bố nhiệt độ, không chỉ là biến động ngẫu nhiên mà là thay đổi hệ thống do không khí lạnh.

    Tổng thể, sự giảm mạnh nhiệt độ này không chỉ ảnh hưởng đến sinh hoạt hàng ngày (người dân bắt đầu mặc ấm hơn) mà còn báo hiệu mùa đông sắp tới, với nguy cơ sương mù và mưa phùn tăng cao.
    """)

    st.header("2. Tốc độ và hướng gió: Bằng chứng của gió mùa Đông Bắc")
    st.markdown("""
    Gió mùa Đông Bắc là "nhân vật chính" trong câu chuyện chuyển mùa. Dữ liệu cho thấy sự thay đổi rõ rệt ở `wind_speed` (tốc độ gió) và `wind_deg` (hướng gió), đặc biệt từ ngày 21/10/2025.

    **Tốc độ gió (wind_speed):** Ở đầu dữ liệu (ngày 18/10), tốc độ gió ở mức thấp, khoảng 2-4 m/s. Đến ngày 21/10, tốc độ tăng lên 4-6.8 m/s tại Hà Nội (cao điểm 6.8 m/s) và 4-5.66 m/s tại Hải Phòng. Sự tăng này (gấp đôi) là dấu hiệu của gió mùa mạnh mẽ.

    **Hướng gió (wind_deg):** Ban đầu, hướng gió chủ yếu từ 130-159° (Đông Nam đến Nam Đông Nam), điển hình cho gió mùa hè. Từ ngày 21/10, hướng chuyển sang 10-33° (Bắc đến Đông Bắc), chính xác là hướng của gió mùa Đông Bắc. Sự chuyển hướng này xác nhận khối không khí lạnh từ lục địa đang tràn xuống.
    """)

    st.header("3. Độ ẩm và thời tiết hanh khô: Biểu hiện của mùa đông")
    st.markdown("""
    Độ ẩm (humidity) là chỉ số quan trọng để nhận biết sự chuyển từ mùa hè ẩm ướt sang mùa đông hanh khô.

    **Phân tích tổng quát:** Ở ngày 18/10, độ ẩm tại Hà Nội (51-67%) và Hải Phòng (58-66%) là mức cao của mùa hè. Đến ngày 21/10, độ ẩm tại Hà Nội tăng tạm thời lên 72% (do sương mù) nhưng giảm xuống 61% vào tối. Tại Hải Phòng, độ ẩm giảm ổn định từ 68% xuống 57-60%. 
    
    **Phân tích từ biểu đồ Area Plot (Độ ẩm):** Biểu đồ diện tích độ ẩm "co lại" về cuối dữ liệu. Sự giảm độ ẩm kết hợp với gió Đông Bắc mạnh làm tăng cảm giác khô lạnh, điển hình cho mùa đông miền Bắc.
    """)