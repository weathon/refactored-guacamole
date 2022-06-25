# Author: Wenqi Guoh
# Co-Au: GitHub Copilot

from typing import Union
from fastapi import FastAPI
import pylab
import haversine as hs

app = FastAPI()


activeDrivers = {}
onCallDrivers = {}

hospitals = [
      {
        "ID": "1",
        "name": "Body Repair",
        "price": 100,
        "capacity": 50,
        "latitude": 38.898556,
        "longitude": -92.338851,
        "type": "hospital"
    },
    {
        "ID": "2",
        "name": "ABC Hospital",
        "price": 100,
        "capacity": 80,
        "latitude": 38.198556,
        "longitude": -92.348851,
        "type": "hospital"
    },
    {
        "ID": "3",
        "name": "Cahot Clinic",
        "price": 100,
        "capacity": 30,
        "latitude": 38.818556,
        "longitude": -92.488851,
        "type": "clinic"
    }
]

class Driver:
    def __init__(self, id, lat, long, Dtype):
        self.id = id
        self.lat = lat
        self.long = long
        self.type = Dtype # 传染病/somewhat engerency
        self.stat = None

def passwordCheck(id, psw):
    return True

@app.post("/driver/reportLocation")
def fun(id, psw, lat, long, Dtype):
    try:
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
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
        return {"status": "error", "message": str(e)}
    

@app.post("/driver/stopStat")
def fun(id, psw):
    try:
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
        if id in activeDrivers.keys():
            activeDrivers[id].stat = "stop"
        return {"status": "success"} 
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/patient/getHospitals")
def fun(id, psw, lat: float, long: float):
    try:
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
        ans = []
        distances = []
        for hospital in hospitals:
            dis = hs.haversine((float(lat), float(long)),(hospital["latitude"], hospital["longitude"]))
            distances.append(dis)
            hospital["distance"] = dis
            ans.append(hospital)
        indexes = pylab.np.argsort(distances)
        ans = pylab.np.array(ans)[indexes]
        
        return {"status": "success", "hospitals": list(ans)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/driver/amiOnCall")
def fun(id, psw):
    if not passwordCheck(id, psw):
        return {"status": "fail", "reason": "password error"}
    if id in onCallDrivers.keys():
        return {"status": "success", "onCall": True, "info": onCallDrivers[id]}
    else:
        return {"status": "success", "onCall": False}


@app.post("/patient/getDriver")
def fun(id, psw, paLat: float, paLong: float, hospitalID):
    # try:
        for i in range(len(hospitals)):
            if hospitals[i]["ID"] == hospitalID:
                hospital = hospitals[i]
                break
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
        ans = []
        distances = []
        for driver in activeDrivers.values():
            if driver.stat == "active":
                dis = hs.haversine((paLat, paLong),(float(driver.lat), float(driver.long)))
                distances.append(dis)
                ans.append(driver)
        if len(ans) == 0:
            return {"status": "fail", "reason": "no driver available"}

        indexes = pylab.np.argsort(distances)
        ans = pylab.np.array(ans)[indexes]
        if len(ans) == 0:
            return {"status": "fail", "reason": "no driver available"}
        cloestDriver = ans[0]
        onCallDrivers[cloestDriver.id] = {"lat":paLat, "long":paLong, "hospitalID":hospitalID}
        activeDrivers[cloestDriver.id].stat = "onCall"
        return {"status": "success", "driver": cloestDriver, "distance": distances[0]}

    # except Exception as e:
    #     return {"status": "error", "message": str(e)}