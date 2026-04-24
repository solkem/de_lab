from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import job  # noqa: F401
from app.models import notebook  # noqa: F401
from app.models import pipeline  # noqa: F401
from app.services.bootstrap import seed_default_catalogs, seed_default_compute


app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_catalogs(db)
        seed_default_compute(db)


app.include_router(router, prefix="/api")
