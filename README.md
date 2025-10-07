# Weather Data Pipeline

Một pipeline đơn giản thu thập dữ liệu thời tiết, lưu vào cơ sở dữ liệu và cung cấp một dashboard/điểm khởi động để xem dữ liệu. README này hướng dẫn cách cài đặt, chạy và triển khai bằng Docker.

## Tổng quan

Dự án chứa một bộ script Python để:
- Lấy dữ liệu thời tiết từ nguồn (fetch)
- Tạo các bảng cần thiết trong database
- Lên lịch thu thập định kỳ (scheduler)
- Cung cấp một dashboard đơn giản để xem/kiểm tra dữ liệu

Mục tiêu: minh họa pipeline ETL nhỏ để thu thập và lưu trữ dữ liệu thời tiết, dễ chạy cục bộ hoặc trong container.

## Cấu trúc chính

- `Dockerfile` - image Python để chạy các script (được dùng bởi docker-compose khi cần)
- `docker-compose.yml` - (nếu có cấu hình dịch vụ) dùng để dựng stack
- `requirements.txt` - các dependencies Python cần cài
- `test_connect.py` - script kiểm tra kết nối (ví dụ tới DB)
- `scripts/`
  - `create_tables.py` - tạo các bảng trong DB
  - `fetch_weather_data.py` - script lấy dữ liệu thời tiết và lưu vào DB
  - `weather_scheduler.py` - scheduler để gọi `fetch_weather_data.py` định kỳ
  - `dashboard.py` - script/dự án nhỏ để hiển thị hoặc thử nghiệm dữ liệu
  - `weather_scheduler.log` - log của scheduler (nếu có)

> Ghi chú: README mô tả chức năng chung mà không thay đổi code; kiểm tra chi tiết bên trong `scripts/` để biết biến môi trường và cấu hình cần thiết.

## Yêu cầu

- Python 3.9+ (Dockerfile dùng base `python:3.9`)
- Các package trong `requirements.txt`
- Một cơ sở dữ liệu (Postgres, MySQL hoặc SQLite tuỳ cách implement trong scripts). Kiểm tra file `scripts/create_tables.py` để xem DB driver và chuỗi kết nối mong đợi.

## Cài đặt và chạy cục bộ

1. Clone repository và chuyển vào thư mục dự án.

2. Tạo virtual environment và cài dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Cấu hình biến môi trường / chuỗi kết nối đến DB

Thêm các biến môi trường cần thiết (ví dụ `DATABASE_URL` hoặc các tham số kết nối). Kiểm tra `scripts/create_tables.py` và `scripts/fetch_weather_data.py` để biết tên biến mà script sử dụng.

4. Tạo bảng trong DB:

```powershell
python scripts\create_tables.py
```

5. Chạy lấy dữ liệu thủ công:

```powershell
python scripts\fetch_weather_data.py
```

6. Chạy scheduler (thu thập định kỳ):

```powershell
python scripts\weather_scheduler.py
```

7. Kiểm tra kết nối (nếu có):

```powershell
python test_connect.py
```

8. Dashboard thử nghiệm:

```powershell
python scripts\dashboard.py
```

## Chạy với Docker

Dockerfile đã chuẩn bị image Python và copy toàn bộ `scripts/` vào `/app/scripts`.

1. Xây image và chạy container (tùy chọn):

```powershell
docker build -t weather-pipeline:latest .
docker run --rm -e DATABASE_URL="<your-db-url>" weather-pipeline:latest python /app/scripts/fetch_weather_data.py
```

2. Hoặc dùng `docker-compose.yml` nếu đã cấu hình sẵn dịch vụ (ví dụ DB + app):

```powershell
docker-compose up --build
```

Ghi chú: bạn cần truyền đúng biến môi trường/volume cấu hình để container có thể kết nối tới DB.

## Logging

Scheduler ghi log vào `scripts/weather_scheduler.log` (nếu được bật trong code). Theo dõi file này để debug lịch chạy.

## Cách debug / kiểm tra nhanh

- Kiểm tra phiên bản Python: `python --version`
- Kiểm tra pip packages: `pip freeze`
- Nếu có lỗi kết nối, kiểm tra biến môi trường chuỗi kết nối và quyền truy cập mạng giữa container và DB

## Gợi ý cải tiến (next steps)

- Thêm file `.env.example` mô tả biến môi trường cần thiết
- Viết tests cho các module ETL
- Thêm CI (GitHub Actions) để chạy lint và tests
- Triển khai dashboard web (Flask/FastAPI) để hiển thị dữ liệu

## License

Đặt license phù hợp với dự án của bạn (ví dụ MIT). Hiện chưa có file license trong repository.

---

Nếu bạn muốn, tôi có thể:
- Tạo file `.env.example` chứa biến môi trường mẫu
- Viết README chi tiết hơn bằng cách đọc nội dung từng script để điền chính xác biến môi trường và ví dụ kết nối

Cho tôi biết bạn muốn tôi mở rộng phần nào nữa.
