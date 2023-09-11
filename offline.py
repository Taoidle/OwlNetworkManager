import shutil
import subprocess
import os
import json
from fastapi import File
from config import OFFLINE_RECEIVE_DIR as offline_dir
from config import OFFLINE_UPLOAD_DIR as upload_dir
from config import OFFLINE_WORKSPACE as workspace_path
from config import OFFLINE_CONF as conf_path
import zipfile
from sql import Sqlite

class Offline:
    _instance = None
    _sql = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._sql = Sqlite()
        return cls._instance

    def __int__(self):
        pass

    async def getOfflineList(self):
        data = []
        for item in self._sql.cursor.execute('''SELECT ID, NAME from OFFLINE'''):
            data.append({"id": item[0], "name": item[1]})
        print("data: ", data)
        return data

    async def getOfflineSettings(self):
        json_file = open(conf_path, 'r', encoding='utf-8')
        conf = json.load(json_file)
        json_file.close()
        return conf

    async def runOffline(self, id: int):
        sql_str = "SELECT ADDRESS, MAIN from OFFLINE where ID=" + str(id)
        data = self._sql.cursor.execute(sql_str).fetchall()[0]
        address = data[0]
        main = data[1]
        # https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
        await OfflineProcess().popen("exec python3 " + address + main)
        return {"statusCode": "200", "status": "success"}

    async def killOffline(self):
        await OfflineProcess().kill()
        os.system("curl \'http://127.0.0.1:23338/cmd\' -H \"Content-Type:application/json\" -H \'Authorization:bearer\' -X POST -d \'{\"cmdId\":12,\"clientId\":1,\"packageId\":1}\'")
        return {"statusCode": "200", "status": "success"}

    async def setOffline(self, id: int, run: bool):
        sql_str = "SELECT ADDRESS, MAIN from OFFLINE where ID=" + str(id)
        data = self._sql.cursor.execute(sql_str).fetchall()[0]
        address = data[0]
        main = data[1]
        with open(conf_path, "w", encoding='utf-8') as f:
            f.write(json.dumps({"id": id, "run": run, "address": address, "main": main}, ensure_ascii=False))
        f.close()
        return {"statusCode": "200", "status": "success"}

    async def saveUpload(self, file: File):
        file_data = await file.read()
        if await self.__saveOfflineFile(file_data, file.filename):
            return await self.__saveUpload(file.filename)

    async def __saveUpload(self, filename: str):
        zip_file = zipfile.ZipFile(offline_dir + filename, "r")
        for file_item in zip_file.namelist():
            zip_file.extract(file_item, upload_dir)
        zip_file.close()
        if os.path.exists(upload_dir + "offline.conf"):
            json_file = open(upload_dir + "offline.conf", 'r', encoding='utf-8')
            offline_conf = json.load(json_file)
            offline_main = offline_conf["main"]
            if os.path.exists(upload_dir + offline_main):
                offline_name = offline_conf["name"]
                offline_id = self._sql.cursor.execute('''SELECT COUNT(ID) FROM OFFLINE''').fetchall()[0][0]
                if offline_id == 0:
                    offline_id = 1
                else:
                    offline_id = self._sql.cursor.execute('''SELECT MAX(ID) FROM OFFLINE''').fetchall()[0][0] + 1
                offline_path = workspace_path + str(offline_id) + '/'
                self._sql.cursor.execute("INSERT INTO OFFLINE (ID, NAME, ADDRESS, MAIN) VALUES (?,?,?,?)", (offline_id, offline_name, offline_path, offline_main))
                self._sql.conn.commit()
                json_file.close()
                os.system("mkdir -p " + workspace_path + str(offline_id))
                os.system("mv " + upload_dir + "/* " + workspace_path + str(offline_id) + "/")
            else:
                await self.__deleteUploadFiles(filename)
                return {"statusCode": "400", "status": "failed"}
        else:
            await self.__deleteUploadFiles(filename)
            return {"statusCode": "400", "status": "failed"}

    async def __saveOfflineFile(self, data: bytes, filename: str) -> bool:
        try:
            save_file = open(offline_dir + filename, "wb+")
            save_file.write(data)
            save_file.close()
            return True
        except IOError:
            return False

    async def __deleteUploadFiles(self, filename: str):
        os.remove(upload_dir + filename)
        shutil.rmtree(upload_dir)
        os.mkdir(upload_dir)


class OfflineProcess:
    _instance = None
    _subp = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __int__(self):
        pass

    async def popen(self, cmd: str):
        self._subp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    async def poll(self):
        return self._subp.poll()

    async def kill(self):
        self._subp.kill()

    async def terminate(self):
        self._subp.terminate()
