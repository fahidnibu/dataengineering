from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState , RunResultState
import os
import time

client = WorkspaceClient(
    host=os.environ["DATABRICKS_HOST"],
    token=os.environ["DATABRICKS_TOKEN"]
)
job_trigger = client.jobs.run_now(
    job_id=os.environ["DATABRICKS_CDC_JOB_ID"]
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