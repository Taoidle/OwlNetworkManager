import json
from fastapi import FastAPI, Query, UploadFile, File
from pydantic import BaseModel
from typing import Union
from network import NetWork
from ota import Ota
from offline import Offline
from env import Env
from starlette.middleware.cors import CORSMiddleware


class WiFi(BaseModel):
    ssid: Union[str, None] = Query(default=None, regex="^[0-9a-zA-Z_-]{1,}$")
    passwd: Union[str, None] = Query(default=None, min_length=8, max_length=32, regex="^[0-9a-zA-Z_-]{1,}$")


class ReWiFi(WiFi):
    reset: bool


class OfflineRun(BaseModel):
    id: int


class OfflineSetting(OfflineRun):
    run: bool


class EnvTable(BaseModel):
    offset: int
    limit: int


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  # 允许跨域的headers，可以用来鉴别来源等作用。


@app.head("/")
async def root():
    return {"message": "ok"}


@app.get("/")
async def root():
    return {"message": "ok"}


@app.get("/api/version")
async def getVersion():
    json_file = open("./VERSION", 'r', encoding='utf-8')
    version = json.load(json_file)
    json_file.close()
    return version


@app.get("/api/status")
async def getStatus():
    return NetWork().getNetworkStatus()


@app.get("/api/list")
async def getWifiList():
    return NetWork().getNetworkWiFiList()


@app.get("/api/reset")
async def resetWiFi():
    NetWork().resetWiFi()


@app.get("/api/rescan")
async def rescanWiFi():
    NetWork().rescanWiFiList()


@app.post("/api/wifi")
async def connectWiFi(wifi: WiFi):
    NetWork().setNetworkWifi(wifi.ssid, wifi.passwd)


@app.post("/api/update")
async def otaUpdate(file: UploadFile = File(...)):
    split_list = file.filename.split('.')
    print(split_list[len(split_list) - 1])
    if split_list[len(split_list) - 1] == "zip":
        return await Ota().update(file)
    else:
        return {"statusCode": "400", "status": "failed", "message": "files type is not zip"}


@app.get("/api/owl_restart")
async def owlRestart():
    NetWork().restartOwlService()


@app.get("/api/offline/list")
async def getOfflineList():
    return await Offline().getOfflineList()


@app.get("/api/offline/settings")
async def getOfflineSettings():
    return await Offline().getOfflineSettings()


@app.post("/api/offline/upload")
async def offlineUpload(file: UploadFile = File(...)):
    split_list = file.filename.split('.')
    print(split_list[len(split_list) - 1])
    if split_list[len(split_list) - 1] == "zip":
        return await Offline().saveUpload(file)
    else:
        return {"statusCode": "400", "status": "failed", "message": "files type is not zip"}


@app.post("/api/offline/update")
async def offlineUpdate(setting: OfflineSetting):
    return await Offline().setOffline(setting.id, setting.run)


@app.post("/api/offline/run")
async def offlineRun(run: OfflineRun):
    return await Offline().runOffline(run.id)


@app.get("/api/offline/kill")
async def offlineKill():
    return await Offline().killOffline()


@app.post("/api/env/list/python")
async def getEnvListPython(data: EnvTable):
    return await Env().getEnvListPython(data.offset, data.limit)


@app.post("/api/env/list/cpp")
async def getEnvListCpp(data: EnvTable):
    return await Env().getEnvListCpp(data.offset, data.limit)


@app.post("/api/env/list/ospkg")
async def getEnvListOsPkg(data: EnvTable):
    return await Env().getEnvListOsPkg(data.offset, data.limit)


@app.get("/api/env/reload/python")
async def envReloadPython():
    return await Env().envReloadPython()


@app.get("/api/env/reload/cpp")
async def envReloadPython():
    return await Env().envReloadCpp()


@app.get("/api/env/reload/ospkg")
async def envReloadOsPkg():
    return await Env().envReloadPkg()


@app.post("/api/env/python/update")
async def envUpdatePython(file: UploadFile = File(...)):
    split_list = file.filename.split('.')
    print(split_list[len(split_list) - 1])
    if split_list[len(split_list) - 1] == "zip":
        return await Env().saveUpload(file)
    else:
        return {"statusCode": "400", "status": "failed", "message": "files type is not zip"}
