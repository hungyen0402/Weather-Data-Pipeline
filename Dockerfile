# Sử dụng image Python làm base
FROM python:3.9

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ thư mục scripts vào /app/scripts
COPY scripts/ /app/scripts/

# Chạy lệnh mặc định (sẽ bị ghi đè bởi command trong docker-compose.yml)
CMD ["python", "-c", "while True: import time; time.sleep(3600)"]