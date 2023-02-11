from fastapi import FastAPI
from pydantic import BaseModel
import network as net


class WiFi(BaseModel):
    ssid: str
    passwd: str


class ReWiFi (WiFi):
    reset: bool


app = FastAPI()


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/api/status")
def getStatus():
    return net.getNetworkStatus()


@app.get("/api/list")
def getWifiList():
    return net.getNetworkWiFiList()


@app.get("/api/rescan")
def rescanWiFi():
    return net.rescanWiFiList()


@app.post("/api/wifi")
def connectWiFi(wifi: WiFi):
    net.setNetworkWifi(wifi.ssid, wifi.passwd)
