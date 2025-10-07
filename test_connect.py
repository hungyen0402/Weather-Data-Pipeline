from sqlalchemy import create_engine
import pandas as pd
import os 
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

df = pd.read_sql("SELECT 1;", engine)
print(df)
