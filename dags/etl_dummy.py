from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.docker_operator import DockerOperator

default_args = {
    "start_date": datetime(2019, 11, 14),
    "owner": "shawe",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "elt-dummy-tutorial", default_args=default_args, schedule_interval="@hourly"
) as dag:
    # Volumes mounted to the docker container
    output_dir = "/usr/local/share"

    def make_etl_operator(task_id: str, operation: str):
        cmd = f"'etl --out-dir {output_dir} {operation}'"
        return DockerOperator(
            command=cmd,
            environment={"PYTHONUNBUFFERED": 1},
            task_id=task_id,
            image=f"etl-dummy:latest",
            volumes=[f"/usr/local/share:{output_dir}"],
            auto_remove=True,
        )

    extract = make_etl_operator(
        "extract-step-dummy-etl", "extract --url http://etl.dummy.com/api/data"
    )
    transform = make_etl_operator("transform-step-dummy-etl", "transform --lower")
    load = make_etl_operator("load-step-dummy-etl", "load --db 9000://fake-db")

    extract >> transform >> load
