from fastapi import FastAPI
from database import Base, engine
from routers import tasks

app = FastAPI()

Base.metadata.create_all(bind=engine)

