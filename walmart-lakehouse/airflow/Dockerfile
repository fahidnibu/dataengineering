FROM apache/airflow:3.3.0

ARG AIRFLOW_VERSION=3.3.0
ARG PYTHON_VERSION=3.13

# Packages DAG code imports go into Airflow's own environment. The constraints file
# is not optional here: without it a transitive dep can downgrade Airflow's core pins.
COPY requirement-airflow.txt /home/airflow/requirement-airflow.txt
RUN pip install --no-cache-dir -r /home/airflow/requirement-airflow.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# dbt goes into its own virtualenv, deliberately NOT into Airflow's site-packages.
# dbt-core pins pydantic, packaging and more-itertools BELOW the versions this image
# ships, so a plain `pip install -r` silently downgrades them and breaks the
# scheduler. Tasks reach dbt through PATH (appended below) or by absolute path.
#
# No compiler layer here on purpose: every dep in requirement.txt resolves to a
# wheel. If you add one that needs to build from source, install gcc as root first.
COPY requirement.txt /home/airflow/dbt-requirement.txt

RUN python -m venv /home/airflow/dbt-venv \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir --upgrade pip \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir \
       -r /home/airflow/dbt-requirement.txt

# Appended, never prepended: prepending would shadow Airflow's own `python`.
ENV PATH="${PATH}:/home/airflow/dbt-venv/bin"
