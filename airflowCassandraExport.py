from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import csv
from cassandra.cluster import Cluster

def export_from_cassandra(**kwargs):
    # Cassandra connection details
    cluster = Cluster(['localhost'])  # Update with your Cassandra host(s)
    session = cluster.connect('people_db')
    query = "SELECT * FROM people"
    rows = session.execute(query)
    columns = rows.column_names

    # Write to CSV
    with open('/home/ubuntu/airflow/data/people_exported.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)

    session.shutdown()
    cluster.shutdown()

default_args = {
    'start_date': datetime(2024, 1, 1),
    'catchup': False,
}

with DAG(
    dag_id='cassandra_export',
    default_args=default_args,
    schedule_interval=None,
    description='Export data from Cassandra people_db.people to CSV',
    tags=['cassandra', 'export'],
) as dag:

    export_task = PythonOperator(
        task_id='export_people_table',
        python_callable=export_from_cassandra,
        provide_context=True,
    )