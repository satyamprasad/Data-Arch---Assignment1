from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import csv
from cassandra.cluster import Cluster
import uuid

def load_csv_to_cassandra(**kwargs):
    csv_file = '/home/ubuntu/airflow/data/people_import_data.csv'
    cluster = Cluster(['localhost'])  # Update with your Cassandra host(s)
    session = cluster.connect('people_db')

    # Assuming the table 'people' exists with appropriate columns
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Adjust columns as per your table schema
            session.execute(
                """
                INSERT INTO people (id, name, age)
                VALUES (%s, %s, %s)
                """,
                (uuid.uuid4(), row['name'], int(row['age']))
            )
    session.shutdown()
    cluster.shutdown()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='cassandraImport',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    import_task = PythonOperator(
        task_id='load_csv_to_cassandra',
        python_callable=load_csv_to_cassandra,
        provide_context=True,
    )