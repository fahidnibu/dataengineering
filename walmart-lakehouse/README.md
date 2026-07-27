# project_dbt — Walmart lakehouse (Airflow + dbt + Databricks)

Medallion-architecture pipeline: CDC out of an operational Postgres into Databricks
bronze, incrementally loaded to silver with dbt, then modelled into a One Big Table
and a star schema in gold — orchestrated end to end by Airflow.

## High-level design

![High-level design](docs/hld.png)

| stage | what happens | where |
|---|---|---|
| **Source** | Operational Postgres, user-facing | `walmart` (external) |
| **CDC ingest** | Databricks job triggered by Airflow, incremental load | `walmart.bronze` |
| **Silver (`silver_t`)** | Per-table cleanup, incremental `MERGE` on `updated_timestamp` | `walmart.silver_t` |
| **Silver (`silver_b`)** | One Big Table — joined/denormalised | `walmart.silver_b` |
| **Quality checks** | dbt tests (`not_null`, `unique`, accepted ranges) | — |
| **Gold** | Star schema: snapshot dimensions + fact table | `walmart.gold` |

Airflow (`airflow/dags/orchestrate.py`) drives the whole sequence: trigger CDC →
`dbt source freshness` → silver_t → test → silver_b → test → gold ephemeral →
snapshots → fact.

## Layout

- [`walmart_projest/`](walmart_projest/) — the dbt project (`dbt-core 1.11.x`, `dbt-databricks 1.12.x`)
- [`airflow/`](airflow/) — local Airflow 3.3 stack (CeleryExecutor) via Docker Compose
- Python env managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`)

## Running Airflow locally

```bash
cp airflow/.env.example airflow/.env      # then fill in the values it lists
cd airflow && docker compose up -d --build
```

UI at http://localhost:8080 (`airflow` / `airflow`).

The image installs dbt into an **isolated virtualenv** (`/home/airflow/dbt-venv`)
rather than alongside Airflow — dbt-core pins `pydantic`/`packaging` below what
Airflow 3.3 ships, so a shared install breaks the scheduler. Consequence worth
remembering: **DAG code cannot `import` anything from that venv.**

- `airflow/requirement.txt` → the dbt venv (dbt CLI only)
- `airflow/requirement-airflow.txt` → Airflow's own env (anything a DAG imports)

Your host `~/.dbt` is mounted read-only into the containers, so the Databricks token
stays on your machine and never enters the image or git.

## Setup on a new machine

### 1. Prerequisites
- Python 3.12 (see `.python-version`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/):
  `curl -LsSf https://astral.sh/uv/install.sh | sh`
- git

### 2. Clone
```bash
git clone <REPO_URL> project_dbt
cd project_dbt
```

### 3. Install dependencies (creates .venv from uv.lock)
```bash
uv sync
```

### 4. Configure Databricks credentials (NOT in git)
The connection profile is intentionally **not** committed (it holds a token).
Copy the template into your dbt home and fill in host + token:
```bash
mkdir -p ~/.dbt
cp profiles.example.yml ~/.dbt/profiles.yml
# edit ~/.dbt/profiles.yml → set host, http_path, token
```
- **host / http_path**: Databricks → SQL Warehouse → *Connection details*
- **token**: Databricks → *User Settings → Developer → Access tokens*

### 5. Install dbt packages (dbt_utils)
```bash
cd walmart_projest
uv run dbt deps
```

### 6. Verify the connection
```bash
uv run dbt debug
```
Expect `All checks passed!`.

### 7. Build and test
```bash
uv run dbt run     # build silver models into walmart.silver_t
uv run dbt test    # run not_null / unique / accepted_range tests
```

## Notes
- Run all `dbt` commands from inside `walmart_projest/` (where `dbt_project.yml` lives).
- `uv run dbt ...` uses the project venv without needing to activate it.
  (Or `source .venv/bin/activate` once, then just `dbt ...`.)
- Models under `models/source/` are written to schema `silver_t` (see the
  `generate_schema_name` override in `walmart_projest/macros/custom_schema.sql`).
- Incremental models: if you change a model's columns, rebuild it once with
  `uv run dbt run --select <model> --full-refresh`.
