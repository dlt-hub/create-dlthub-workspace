# Recent merges on `devel`

## #1 — MotherDuck as the starter `prod` destination + pipeline fixes

- `prod` env now defaults to MotherDuck; `dev` stays on local duckdb.
- New `.dlt/prod.secrets.toml` template with token instructions; `pyproject.toml` adds the `motherduck` extra.
- `starter_transformations.py` reads upstream data via `dlt.attach(...)` instead of importing `starter_pipe` (importing it had the side effect of re-instantiating the ingestion pipeline).
- Removed `.dlt/access.config.toml` and the dead `[destination.warehouse]` block in `.dlt/config.toml`.
- Next-steps panel adds a "paste your MotherDuck token" step.
- `CONTRIBUTING.md` documents the `git add -f` workaround for shipped scaffold templates that match the workspace `.gitignore`.

## #2 — Ship all available toolkits in the starter scaffold

- `config.py:TOOLKITS` expanded from 4 to 8: added `data-quality`, `dlthub-platform`, `filesystem-pipeline`, `sql-database-pipeline`.
- `make generate-ai` regenerated the bundled AI workbench files against `WORKBENCH_REF`. The resulting scaffold diff (new skill dirs under `.agents/`, updated `.dlt/.toolkits`, updated `AGENTS.md`) is committed so `check-ai` stays green.

### Note for follow-up
`pyproject.toml` is intentionally not touched by `generate-ai`. If any of the new toolkits expect additional Python deps (e.g. `sql-database-pipeline` → `sqlalchemy`, `filesystem-pipeline` → `s3fs`), those must be added to `scaffolds/starter_workspace/pyproject.toml` by hand.
