# LakeForge API

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

API endpoints available in Phase 1:

- `GET /api/health`
- `GET /api/catalogs`
- `GET /api/compute`
- `GET /api/jobs`
- `GET /api/jobs/{id}`
- `GET /api/jobs/{id}/runs`
- `POST /api/jobs`
- `POST /api/jobs/{id}/run`
- `GET /api/pipelines`
- `GET /api/pipelines/{id}`
- `GET /api/pipelines/{id}/runs`
- `GET /api/pipelines/runs/{id}`
- `POST /api/pipelines`
- `POST /api/pipelines/{id}/run`
- `GET /api/lineage`
- `GET /api/notebooks`
- `GET /api/notebooks/{id}`
- `GET /api/notebooks/{id}/runs`
- `POST /api/notebooks`
- `POST /api/notebooks/{id}/execute`
- `GET /api/tables`
- `POST /api/tables`
- `GET /api/tables/{catalog}/{schema}/{table}`
- `GET /api/tables/{catalog}/{schema}/{table}/history`
- `GET /api/runtime/spark`
