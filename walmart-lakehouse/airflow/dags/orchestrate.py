from airflow.sdk import dag, task
from airflow.operators.bash import BashOperator

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState , RunResultState
import os
import time

# Supplied by airflow/.env (gitignored) via the compose `env_file`. See .env.example.
DATABRICKS_HOST = os.environ["DATABRICKS_HOST"]
DATABRICKS_TOKEN = os.environ["DATABRICKS_TOKEN"]
DATABRICKS_CDC_JOB_ID = os.environ["DATABRICKS_CDC_JOB_ID"]

@dag
def orchestrate():
    @task
    def ingest_cdc():
        client = WorkspaceClient(
            host=DATABRICKS_HOST,
            token=DATABRICKS_TOKEN
        )
        job_trigger = client.jobs.run_now(
            job_id=DATABRICKS_CDC_JOB_ID
        )
        print(f"Triggered Databricks job with run ID: {job_trigger.run_id}")

        while True:
            run_status = client.jobs.get_run(run_id=job_trigger.run_id)
            print(f"Current job status: {run_status.state.life_cycle_state}, Result state: {run_status.state.result_state}")
            if run_status.state.life_cycle_state in [RunLifeCycleState.TERMINATED, RunLifeCycleState.SKIPPED, RunLifeCycleState.INTERNAL_ERROR]:
                print("Job failed or was skipped.")
                if run_status.state.result_state == RunResultState.SUCCESS:
                    print("Job completed successfully.")
                    break
                else:
                    raise Exception(f"Result state: {run_status.state.result_state}")
            time.sleep(5)  # Wait for 10 seconds before checking again
            return "Ingesting CDC data..."
        

    @task.bash
    def clean_target():
        return "rm -rf /opt/airflow/walmart_projest/target/* && rm -rf /opt/airflow/walmart_projest/logs/*"
    
    @task.bash
    def source_freshness():
        return "cd /opt/airflow/walmart_projest && dbt source freshness"
    
    silver_t = BashOperator(
        task_id='silver_t',
        bash_command='cd /opt/airflow/walmart_projest && dbt run --select silver_t'
    )

    silver_t_test = BashOperator(
        task_id='silver_t_test',
        bash_command='cd /opt/airflow/walmart_projest && dbt test --select silver_t'
    )   

    silver_b = BashOperator(
        task_id='silver_b',
        bash_command='cd /opt/airflow/walmart_projest && dbt run --select silver_b'
    )

    silver_b_test = BashOperator(
        task_id='silver_b_test',
        bash_command='cd /opt/airflow/walmart_projest && dbt test --select silver_b'
    )

    gold_eph = BashOperator(
        task_id='gold_eph',
        bash_command='cd /opt/airflow/walmart_projest && dbt run --select gold/ephemeral'
    )

    gold_dim = BashOperator(
        task_id='gold_dim',
        bash_command='cd /opt/airflow/walmart_projest && dbt snapshot'
    )

    gold_fact = BashOperator(
        task_id='gold_fact',
        bash_command='cd /opt/airflow/walmart_projest && dbt run --select gold_fact'
    )       


    ingest_cdc() >> clean_target() >> source_freshness() >> silver_t >> silver_t_test >> silver_b >> silver_b_test >> gold_eph >> gold_dim >> gold_fact

orchestrate_dag = orchestrate()
    