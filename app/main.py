from fastapi import FastAPI

from .routers import appointments, organizations, users

app = FastAPI()
app.include_router(appointments.router)
app.include_router(organizations.router)
app.include_router(users.router)

