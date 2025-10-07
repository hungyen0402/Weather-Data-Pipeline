import requests
import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_city_coordinates(city_name, country_code="VN", limit=1):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("WEATHER_API_KEY not found in environment variables")
    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': f"{city_name},{country_code}",
        'limit': limit,
        'appid': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Kiểm tra lỗi
        data = response.json()

        if data and len(data):
            return {
                'lat': data[0]['lat'],
                'lon': data[0]['lon'],
                'city': city_name,
                'country': data[0].get('country', ''),
                'state': data[0].get('state', '')
            }
        else:
            print(f'Không tìm thấy tọa độ cho thành phố: {city_name}')
            return None
    except Exception as e:
        print(f"Error fetching coordinates for {city_name}: {e}")
        return None

def get_weather_data(city_name, country_code="VN"):
    coordinates = get_city_coordinates(city_name, country_code)

    if not coordinates:
        return None

    api_key = os.getenv("WEATHER_API_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': coordinates['lat'],
        'lon': coordinates['lon'],  # Đã sửa từ 'lot'
        'appid': api_key,
        'units': 'metric'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            'city': coordinates['city'],
            'temp': data['main']['temp'],
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather_description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'wind_deg': data['wind'].get('deg', 0),
            'visibility': data.get('visibility', 0),
            'timestamp': datetime.now()
        }
    except Exception as e:
        print(f"Error fetching weather data for {city_name}: {e}")
        return None

def save_weather_database(weather_data):
    if weather_data:
        engine = create_engine(os.getenv("DATABASE_URL"))
        df = pd.DataFrame([weather_data])
        try:
            df.to_sql('weather_data', engine, if_exists='append', index=False)
            print(f"Weather data saved for {weather_data['city']} at {weather_data['timestamp']}")
        except Exception as e:
            print(f"Error saving to database: {e}")
            print("Please update the database table structure")
        finally:
            engine.dispose()  # Đóng kết nối sau khi dùng

def get_all_weather_data():
    cities_info = [
        {"name": "Hanoi", "country": "VN"},
        {"name": "Ho Chi Minh City", "country": "VN"},
        {"name": "Da Nang", "country": "VN"},
        {"name": "Hai Phong", "country": "VN"},
        {"name": "Can Tho", "country": "VN"},
        {"name": "Nha Trang", "country": "VN"}
    ]

    successful_fetches = 0
    for city_info in cities_info:
        weather_data = get_weather_data(city_info["name"], city_info["country"])
        if weather_data:
            save_weather_database(weather_data)
            successful_fetches += 1
        import time
        time.sleep(1)
    print(f"\nCompleted: {successful_fetches}/{len(cities_info)} cities processed successfully")

if __name__ == "__main__":
    get_all_weather_data()