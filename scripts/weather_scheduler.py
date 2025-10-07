from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger 
from fetch_weather_data import get_all_weather_data
import logging
import os 
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BlockingScheduler()
    # add job 
    scheduler.add_job(
        get_all_weather_data,
        trigger='date',
        id='intial',
        name='Thu thập dữ liệu đầu',
        replace_existing=True
    )
    scheduler.add_job(
        get_all_weather_data,
        trigger=IntervalTrigger(seconds=120),
        id='main',
        name='Thu thập dữ liệu thời tiết mỗi 2 tiếng',
        replace_existing=True
    )

    try:
        logger.info("Bắt đầu scheduler...")
        logger.info("Scheduler sẽ chạy mỗi 120 phút")
        logger.info("Nhấn Ctrl+C để dừng")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Dừng scheduler...")
        scheduler.shutdown()

if __name__ == '__main__':
    start_scheduler()
