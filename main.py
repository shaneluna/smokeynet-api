from fastapi import FastAPI, Path
from api.smokeynet_api import SmokeyNetAPI
from enum import IntEnum

app = FastAPI()
smokeynet_api = SmokeyNetAPI()

@app.get("/")
def root():
    return {"Hello": "Mundo"}

@app.get("/camera/weatherdata/{camera_id}")
def get_camera_weatherdata(camera_id: str = Path(None, description="The camera station id to get weather data for.")):
    return {"data": smokeynet_api.get_camera_weatherdata(camera_id)}
