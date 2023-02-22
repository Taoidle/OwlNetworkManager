from fastapi import FastAPI, Query, UploadFile, File
from pydantic import BaseModel
from typing import Union
from network import NetWork
from starlette.middleware.cors import CORSMiddleware


class WiFi(BaseModel):
    ssid: Union[str, None] = Query(default=None, regex="^[0-9a-zA-Z_-]{1,}$")
    passwd: Union[str, None] = Query(default=None, min_length=8, max_length=32, regex="^[0-9a-zA-Z_-]{1,}$")


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
async def root():
    return {"message": "ok"}


@app.get("/api/status")
async def getStatus():
    return NetWork().getNetworkStatus()


@app.get("/api/list")
async def getWifiList():
    return NetWork().getNetworkWiFiList()


@app.get("/api/rescan")
async def rescanWiFi():
    NetWork().rescanWiFiList()


@app.post("/api/wifi")
def connectWiFi(wifi: WiFi):
    net.setNetworkWifi(wifi.ssid, wifi.passwd)
async def connectWiFi(wifi: WiFi):
    NetWork().setNetworkWifi(wifi.ssid, wifi.passwd)
