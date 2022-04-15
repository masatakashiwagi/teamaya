# import pika
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logger import get_logger
from producer import producer

LOGGER = get_logger()

# FastAPI instance
app = FastAPI(title="FastAPI", version="1.0")

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(producer.router)


# For Health Check
@app.get("/")
def health_check():
    """Container Operation & Health Check
    """
    return {"Status": "OK"}
