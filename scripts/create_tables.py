from sqlalchemy import create_engine, Column, Integer, Float, String, TIMESTAMP, MetaData, Table, UniqueConstraint
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL")) # dùng khi chạy ngoài docker, nếu dùng docker thì phải dùng DOCKER_DATABASE_URL
metadata = MetaData()

# Định nghĩa bảng 
weather_data = Table(
    'weather_data', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('city', String(100)),
    Column('temp', Float),
    Column('temp_min', Float),
    Column('temp_max', Float),
    Column('humidity', Integer),
    Column('pressure', Integer),
    Column('wind_speed', Float),
    Column('wind_deg', Integer),
    Column('visibility', Integer),
    Column('weather_description', String(100)),
    Column('timestamp', TIMESTAMP),
    UniqueConstraint('city', 'timestamp', name='unique_city_time')
)
metadata.drop_all(engine)
print("⚠️ Đã xóa toàn bộ bảng cũ trong database.")
metadata.create_all(engine)

print('Bảng weather_data đã được tạo hoặc đã tồn tại sẵn')