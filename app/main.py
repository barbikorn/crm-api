from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.v1 import user, lead, line, log
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


app.include_router(user.router, prefix="/api/v1", tags=["Users"])
app.include_router(lead.router, prefix="/api/v1", tags=["Leads"])
app.include_router(line.router, prefix="/api/v1", tags=["Line"])
app.include_router(log.router, prefix="/api/v1", tags=["Logs"])
