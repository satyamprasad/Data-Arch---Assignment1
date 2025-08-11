from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pymongo import MongoClient
import csv
import os

def export_mongo_to_csv(**kwargs):
    mongo_uri = "mongodb://localhost:27017/"
    db_name = "people_db"
    collection_name = "people"
    export_folder = "/home/ubuntu/airflow/data"
    export_file = os.path.join(export_folder, "people_mongo_export.csv")

    os.makedirs(export_folder, exist_ok=True)

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    documents = list(collection.find())
    if not documents:
        return

    # Get all unique keys for CSV header
    keys = set()
    for doc in documents:
        keys.update(doc.keys())
    keys.discard('_id')  # Optionally remove MongoDB's _id field
    keys = sorted(keys)

    with open(export_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for doc in documents:
            row = {k: doc.get(k, "") for k in keys}
            writer.writerow(row)

default_args = {
    'start_date': datetime(2024, 1, 1),
    'catchup': False,
}

with DAG(
    dag_id='mongoDBExport',
    default_args=default_args,
    schedule_interval=None,
    description='Export MongoDB people collection to CSV',
    tags=['mongo', 'export'],
) as dag:

    export_task = PythonOperator(
        task_id='export_mongo_to_csv',
        python_callable=export_mongo_to_csv,
        provide_context=True,
    )