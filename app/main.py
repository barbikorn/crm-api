from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.v1 import user, lead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM API")

app.include_router(user.router, prefix="/api/v1", tags=["Users"])
app.include_router(lead.router, prefix="/api/v1", tags=["Leads"])
