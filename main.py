# Author: Wenqi Guoh
# Co-Au: GitHub Copilot

from typing import Union
from fastapi import FastAPI, Form
import pylab
import haversine as hs
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://127.0.0.1:8000",
    "*"
]



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


import os 
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

with open("../twilio.txt", "r") as f:
    auth_token = f.readline().strip()
    account_sid = f.readline().strip()
    client = Client(account_sid, auth_token)


SMS = "You got a ride request; please open the App as soon as possible to view the detail. Or click the link to see the route. https://www.google.com/maps/dir/?api=1&destination=%s,%s&waypoints=%s,%s"
def send_message(number, hospitallat, hospitallong, houselat, houselong):
    message = client.messages \
    .create(
         body=SMS % (hospitallat, hospitallong, houselat, houselong),
         from_='+17072895784',
         to='+1' + number
     )

class Driver:
    def __init__(self, id, lat, long, Dtype):
        self.id = id
        self.lat = lat
        self.long = long
        self.type = Dtype # 传染病/somewhat engerency
        self.stat = None


def passwordCheck(id, psw):
    return True

@app.get("/driver/reportLocation")
def fun(id, psw, lat, long, Dtype = 0):
    try:
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
        if id in activeDrivers.keys():
            # already active
            activeDrivers[id].lat = lat
            activeDrivers[id].long = long
            activeDrivers[id].Dtype = Dtype
            # activeDrivers[id].stat = stat
        else:
            # new driver
            activeDrivers[id] = Driver(id, lat, long, Dtype)
            # activeDrivers[id].stat = stat
        return {"status": "success"} 
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.get("/driver/reportStat")
def fun(id, psw, stat):
    try:
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
        if id in activeDrivers.keys():
            activeDrivers[id].stat = stat
        return {"status": "success"} 
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/patient/getHospitals")
def fun(id: str = Form(""), psw: str = Form(""), lat: float= Form(-1), long: float= Form(-1)):
    try:
        if not passwordCheck(id, psw):
            return {"status": "fail", "reason": "password error"}
        ans = []
        distances = []
        for hospital in hospitals:
            dis = hs.haversine((float(lat), float(long)),(hospital["latitude"], hospital["longitude"]))
            distances.append(dis)
            hospital["distance"] = dis
            hospital["Rprice"] = dis * 0.5
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
        return {"status": "success", "onCall": True, "info": onCallDrivers[id], "hospitals": hospitals}
    else:
        return {"status": "success", "onCall": False}

paired = {}

@app.get("/patient/getDistance")
def fun(id, psw):
    # This whole function is generated by copolit
    if not passwordCheck(id, psw):
        return {"status": "fail", "reason": "password error"}
    driverID = paired[id][2]
    dis = hs.haversine((
        float(paired[id][0]),
        float(paired[id][0])
    ),(float(activeDrivers[driverID].lat), float(activeDrivers[driverID].long)))
    return {"status": "success", "distance": dis}

    
@app.post("/patient/getDriver")
def fun(id:  str = Form(""), psw :  str = Form(""), paLat: float= Form(""), paLong: float= Form(""), hospitalID: str = Form("")):
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
                print(driver.lat)
                dis = hs.haversine((paLat, paLong),(float(driver.lat), float(driver.long)))
                distances.append(dis)
                ans.append(driver)
        if len(ans) == 0:
            return {"status": "fail", "reason": "no driver available"}

        indexes = pylab.np.argsort(distances)
        ans = pylab.np.array(ans)[indexes]
        cloestDriver = ans[0]
        onCallDrivers[cloestDriver.id] = {"lat":paLat, "long":paLong, "hospitalID":hospitalID}
        activeDrivers[cloestDriver.id].stat = "onCall"
        send_message(cloestDriver.id, hospital["latitude"], hospital["longitude"], paLat, paLong)
        paired[id] = [paLat, paLong, cloestDriver.id]
        return {"status": "success", "driver": cloestDriver, "distance": distances[0]}

    # except Exception as e:
    #     return {"status": "error", "message": str(e)}



@app.post("/hospital/getList")
def fun(id, psw):
    pass