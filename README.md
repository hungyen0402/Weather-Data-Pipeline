# Weather Data Pipeline

Một pipeline nhỏ thu thập dữ liệu thời tiết (OpenWeatherMap), lưu vào cơ sở dữ liệu PostgreSQL và hiển thị dashboard/analysis bằng Streamlit. README này đã cập nhật để mô tả các script hiện tại, biến môi trường cần thiết và cách chạy cục bộ hoặc bằng Docker Compose.

## Tổng quan

Dự án cung cấp:
- Lấy tọa độ & dữ liệu thời tiết từ OpenWeatherMap (`scripts/fetch_weather_data.py`)
- Tạo/khởi tạo bảng trong DB (`scripts/create_tables.py`) — lưu ý: script hiện drop toàn bộ bảng cũ trước khi tạo lại
- Scheduler để thu thập định kỳ (`scripts/weather_scheduler.py`)
- Dashboard Streamlit (`scripts/dashboard.py`) và trang phân tích chuyên sâu `scripts/pages/phan_tich.py`

Mục tiêu: minh họa một pipeline ETL đơn giản, dễ chạy cục bộ hoặc trong container.

## Cấu trúc chính

- `Dockerfile` - image Python base (python:3.9)
- `docker-compose.yml` - dựng stack gồm Postgres + dashboard + pipeline
- `requirements.txt` - các dependencies Python
- `test_connect.py` - script kiểm tra kết nối (nếu có)
- `scripts/`
  - `create_tables.py` - tạo bảng `weather_data` (chú ý: script drop_all trước khi create_all)
  - `fetch_weather_data.py` - lấy dữ liệu thời tiết từ OpenWeatherMap và lưu vào bảng `weather_data`
  - `weather_scheduler.py` - scheduler (APScheduler) gọi `get_all_weather_data` định kỳ (mặc định mỗi 120 giây)
  - `dashboard.py` - Streamlit app chính để xem dữ liệu
  - `pages/phan_tich.py` - trang phân tích sâu (nhiều biểu đồ, wordcloud, heatmap) — được Streamlit load như một page

> Lưu ý: `scripts/dashboard.py` sử dụng biến môi trường `DATABASE_URL_DASHBOARD` để kết nối; hiện tại docker-compose truyền `DATABASE_URL` cho container. Bạn có thể đặt `DATABASE_URL_DASHBOARD` trùng với `DATABASE_URL` trong `.env` hoặc sửa `dashboard.py` để fallback.
  - `create_tables.py` - tạo các bảng trong DB
  - `fetch_weather_data.py` - script lấy dữ liệu thời tiết và lưu vào DB
  - `weather_scheduler.py` - scheduler để gọi `fetch_weather_data.py` định kỳ
  - `dashboard.py` - script/dự án nhỏ để hiển thị hoặc thử nghiệm dữ liệu
  - `weather_scheduler.log` - log của scheduler (nếu có)

> Ghi chú: README mô tả chức năng chung mà không thay đổi code; kiểm tra chi tiết bên trong `scripts/` để biết biến môi trường và cấu hình cần thiết.


## Yêu cầu

- Python 3.9+ (Dockerfile dùng base `python:3.9`)
- Các package trong `requirements.txt` (ví dụ: requests, python-dotenv, psycopg2-binary, pandas, SQLAlchemy, streamlit, APScheduler, plotly, seaborn, wordcloud)
- PostgreSQL (docker-compose sẽ tạo Postgres 15 nếu bạn dùng compose)

Code hiện tại dùng SQLAlchemy với driver `psycopg2` nên `DATABASE_URL` cần có định dạng `postgresql+psycopg2://user:password@host:port/dbname`.

## Cài đặt và chạy cục bộ (Windows PowerShell)

1. Clone repository và chuyển vào thư mục dự án:

```powershell
cd C:\Users\hoang\Documents\Weather_Data_Pipeline
```

2. Tạo virtual environment và cài dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

3. Tạo file `.env` ở thư mục gốc (xem mẫu bên dưới). Các biến bắt buộc: `WEATHER_API_KEY`, `DATABASE_URL`. Dashboard code hiện sử dụng `DATABASE_URL_DASHBOARD` — tốt nhất đặt nó trùng `DATABASE_URL`.

4. Tạo bảng (chú ý: script sẽ xóa bảng cũ trước khi tạo lại):

```powershell
python .\scripts\create_tables.py
```

5. Lấy dữ liệu thủ công (kiểm tra kết nối API & DB):

```powershell
python .\scripts\fetch_weather_data.py
```

6. Chạy scheduler (thu thập định kỳ):

```powershell
python .\scripts\weather_scheduler.py
```

7. Chạy dashboard Streamlit:

```powershell
streamlit run .\scripts\dashboard.py --server.port 8501 --server.address 0.0.0.0
```

Mở trình duyệt tới http://localhost:8501. Streamlit sẽ tự động phát hiện `scripts/pages/phan_tich.py` và thêm trang phân tích trong UI.

## Chạy với Docker Compose

`docker-compose.yml` trong repo sẽ dựng 3 service:
- `db`: postgres:15 (user=duchung, password=duchung2004@@, db=weather)
- `dashboard`: image build từ `Dockerfile`, chạy Streamlit
- `pipeline`: image build từ `Dockerfile`, chạy `weather_scheduler.py`

1. Tạo file `.env` (xem mẫu bên dưới) ở thư mục gốc.

2. Chạy:

```powershell
docker-compose up --build
```

3. Truy cập dashboard: http://localhost:8501

Lưu ý kỹ thuật quan trọng:
- Trong `docker-compose.yml`, service `db` được đặt tên `db`. Khi containers (dashboard/pipeline) kết nối tới DB nội bộ trong mạng compose, hostname phải là `db` (không phải `localhost`). Mẫu `.env` dưới đây đã dùng `db` làm host.
- Nếu mật khẩu Postgres chứa ký tự `@` (ví dụ `duchung2004@@`), khi viết `DATABASE_URL` theo URL bạn phải percent-encode ký tự `@` thành `%40`. Ví dụ: `duchung2004@@` -> `duchung2004%40%40`.

Ví dụ chạy trong background:

```powershell
docker-compose up -d --build
docker-compose logs -f dashboard
docker-compose logs -f pipeline
```

Tắt và xóa:

```powershell
docker-compose down
```


## Logging

Scheduler ghi log vào `weather_scheduler.log` (file được tạo trong thư mục làm việc container/host tuỳ cách bạn chạy). Kiểm tra file này để debug lịch chạy.

## .env mẫu (copy sang `.env` và chỉnh lại giá trị)

Mẫu dùng cho docker-compose (container kết nối tới service `db`):

```env
# OpenWeatherMap API key
WEATHER_API_KEY=your_openweathermap_api_key_here

# Postgres URL cho containers (host = db - service name trong docker-compose)
# LƯU Ý: nếu mật khẩu chứa ký tự @ thì phải encode: @ -> %40
DATABASE_URL=postgresql+psycopg2://duchung:duchung2004%40%40@db:5432/weather

# Dashboard có thể dùng biến riêng hoặc trùng với DATABASE_URL
DATABASE_URL_DASHBOARD=${DATABASE_URL}
```

Mẫu nếu bạn kết nối tới DB trên máy host (local):

```env
WEATHER_API_KEY=your_openweathermap_api_key_here
DATABASE_URL=postgresql+psycopg2://duchung:duchung2004%40%40@localhost:5432/weather
DATABASE_URL_DASHBOARD=${DATABASE_URL}
```

## Kiểm tra & xử lý lỗi thường gặp

- Nếu thiếu `WEATHER_API_KEY`: các hàm get_* sẽ raise hoặc không trả về dữ liệu. Đặt giá trị trong `.env`.
- Nếu lỗi kết nối DB: kiểm tra `DATABASE_URL` đúng định dạng và host/port có thể truy cập. Với docker-compose, host phải là `db`.
- Nếu Streamlit không thấy trang `phan_tich.py`: chạy Streamlit với thư mục chứa file `dashboard.py` (ví dụ `streamlit run scripts/dashboard.py`) để Streamlit định vị pages trong `scripts/pages/`.
- Nếu bảng rỗng: chạy `python .\scripts\fetch_weather_data.py` một lần để kiểm tra lưu trữ.

## Gợi ý cải tiến (tùy chọn)

- Thêm file `.env.example` vào repo (tôi có thể thêm giúp bạn).
- Cập nhật `scripts/dashboard.py` để fallback `DATABASE_URL_DASHBOARD` -> `DATABASE_URL` nếu biến đầu tiên không tồn tại.
- Thêm tests cho module ETL và CI (GitHub Actions).

---

Nếu bạn muốn, tôi có thể tạo ngay file `.env.example` và/hoặc sửa `scripts/dashboard.py` để fallback tự động — bạn muốn tiếp theo làm gì?
