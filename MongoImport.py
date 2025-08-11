from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
import uuid;

def import_csv_to_mongo():
    # Read CSV file
    df = pd.read_csv('/home/ubuntu/airflow/data/people_import_data.csv')
    records = df.to_dict(orient='records')
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['people_db']
    collection = db['people']
    
    # Insert records
    if records:
        collection.insert_many(records)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='MongoImport',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Import CSV data into MongoDB',
) as dag:

    import_task = PythonOperator(
        task_id='import_csv_to_mongo',
        python_callable=import_csv_to_mongo,
    )