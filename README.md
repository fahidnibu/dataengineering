# project_dbt — Walmart dbt project (Databricks)

dbt project that builds the **silver** layer (`silver_t` schema) on top of the
Databricks **bronze** layer, in the `walmart` catalog.

- Python env is managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).
- The dbt project itself lives in [`walmart_projest/`](walmart_projest/).
- Adapters: `dbt-core 1.11.x`, `dbt-databricks 1.12.x`.

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
