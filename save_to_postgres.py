from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import requests

POSTGRES_HOST = "62.72.21.79"
POSTGRES_PORT = 5433
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "KzKmJQA#io4pTCN"
POSTGRES_DB = "postgres"

# Define the model
Base = declarative_base()


class MyTable(Base):
    __tablename__ = 'notebooks'
    user_id = Column(String)
    created_at = Column(DateTime)
    last_accessed = Column(DateTime)
    notebook_id = Column(String, primary_key=True)
    description = Column(String)
    port = Column(Integer)


# Connect to the database
engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

notebook_id = os.getenv('NOTEBOOK_ID')

# Query for the specific entry
row_count = session.query(MyTable).filter(MyTable.notebook_id == notebook_id).delete(synchronize_session='evaluate')

if row_count > 0:
    session.commit()
else:
    print("Rows not found")


session.close()

response = requests.get(f"http://{os.getenv('SERVICE_NAME')}:{os.getenv('SERVICE_PORT')}")
if response.status_code == 200:

    response = requests.delete(f"http://{os.getenv('SERVICE_NAME')}:{os.getenv('SERVICE_PORT')}/delete_pod?uid={notebook_id}")

    if response.status_code == 200:
        print("Pod deleted successfully!")
