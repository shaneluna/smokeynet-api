from fastapi import FastAPI, Path
from api.smokeynet_api import SmokeyNetAPI
from enum import IntEnum

class Environment(IntEnum):
    DEV = 1
    PROD = 3

#####################
ENV = Environment.DEV
#####################

app = FastAPI()

if ENV == Environment.PROD:
    smokeynet_api = SmokeyNetAPI()
else:
    smokeynet_api = SmokeyNetAPI("./config.yaml")

@app.get("/")
def root():
    return {"Hello": "Mundo"}

@app.get("/camera/weatherdata/{camera_id}")
def get_camera_weatherdata(camera_id: str = Path(None, description="The camera station id to get weather data for.")):
    return {"data": smokeynet_api.get_camera_weatherdata(camera_id)}
