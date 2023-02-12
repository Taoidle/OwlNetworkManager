from fastapi import FastAPI
from pydantic import BaseModel
import network as net
from starlette.middleware.cors import CORSMiddleware

class WiFi(BaseModel):
    ssid: str
    passwd: str


class ReWiFi (WiFi):
    reset: bool


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  #设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  #允许跨域的headers，可以用来鉴别来源等作用。

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
