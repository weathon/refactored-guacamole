# Author: Wenqi Guoh
# Co-Au: GitHub Copilot

from typing import Union

from fastapi import FastAPI

app = FastAPI()


activeDrivers = {}

class Driver:
    def __init__(self, id, lat, long, Dtype):
        self.id = id
        self.lat = lat
        self.long = long
        self.type = Dtype # 传染病/somewhat engerency
        self.stat = None


@app.post("/driver/reportLocation")
def fun(id, psw, lat, long, Dtype):
    try:
        if id in activeDrivers.keys():
            # already active
            activeDrivers[id].lat = lat
            activeDrivers[id].long = long
            activeDrivers[id].Dtype = Dtype
            activeDrivers[id].stat = "active"
        else:
            # new driver
            activeDrivers[id] = Driver(id, lat, long, Dtype)
            activeDrivers[id].stat = "active"
        return {"status": "success"} 
    except Exception as e:
        retutn {"status": "error", "message": str(e)}
    


@app.post("/driver/stopStat")
def fun():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
