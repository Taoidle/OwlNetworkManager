import shutil
import subprocess
import os
from fastapi import File
from config import OTA_RECEIVE_DIR as ota_dir
from config import OTA_SERVICE_LIST as ota_service_list
from config import OTA_PUB_KEY as key_path
from config import OTA_TARGET_FILENAME as update_filename
from config import OTA_UPDATE_DIR as update_dir
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
import base64
import zipfile


class Ota:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pass

    async def update(self, file: File):
        file_data = await file.read()
        if await self.__save_ota_file(file_data, file.filename):
            if await self.__stop_services(ota_service_list):
                if await self.__decode_file(file.filename):
                    if await self.__split_file(file.filename, update_filename):
                        return await self.__update(file.filename)
        else:
            return {"statusCode": "400", "status": "failed"}

    async def __update(self, filename: str):
        zip_file = zipfile.ZipFile(ota_dir + update_filename, "r")
        for file_item in zip_file.namelist():
            zip_file.extract(file_item, update_dir)
        zip_file.close()
        if os.path.exists(update_dir + "ota_update.sh"):
            os.system("chmod a+x " + update_dir + "ota_update.sh")
            if subprocess.Popen("/bin/bash " + update_dir + "ota_update.sh", shell=True, stderr=subprocess.PIPE).stderr.readline().decode('utf-8').strip('\n') != "":
                await self.__delete_ota_files(filename)
                return {"statusCode": "400", "status": "failed"}
            else:
                await self.__delete_ota_files(filename)
                return {"statusCode": "200", "status": "success"}
        else:
            await self.__delete_ota_files(filename)
            return {"statusCode": "400", "status": "failed"}

    async def __delete_ota_files(self, filename: str):
        os.remove(ota_dir + filename)
        os.remove(ota_dir + update_filename)
        shutil.rmtree(update_dir)
        os.mkdir(update_dir)

    async def __decode_file(self, filename: str) -> bool:
        rsa_pub_file = open(key_path, encoding='gbk')
        key = rsa_pub_file.read()
        rsa_key = RSA.importKey(key.encode("utf-8"))
        verifier = PKCS1_v1_5.new(rsa_key)
        digest = SHA256.new()
        file_in = open(ota_dir + filename, "rb+")
        file_data = file_in.read()
        digest.update(file_data[512::])
        is_verify = verifier.verify(digest, base64.b64decode(file_data[0:512]))
        file_in.close()
        rsa_pub_file.close()
        return is_verify

    async def __split_file(self, filename: str, target_name: str) -> bool:
        try:
            file_in = open(ota_dir + filename, "rb+")
            file_data = file_in.read()[512::]
            file_out = open(ota_dir + target_name, "wb+")
            file_out.write(file_data)
            file_out.close()
            file_in.close()
            return True
        except IOError:
            return False

    async def __save_ota_file(self, data: bytes, filename: str) -> bool:
        try:
            save_file = open(ota_dir + filename, "wb+")
            save_file.write(data)
            save_file.close()
            return True
        except IOError:
            return False

    async def __stop_services(self, services_list: list) -> bool:
        check_list = []
        for item in services_list:
            if await self.__stop_service(item): check_list.append(True)
        if len(check_list) == len(services_list): return True
        else: return False

    async def __stop_service(self, service_name: str) -> bool:
        os.system("systemctl stop " + service_name)
        status = subprocess.Popen("systemctl status " + service_name + " | grep Active | awk '{print $2}'", shell=True, stdout=subprocess.PIPE).stdout.readline().decode('utf-8').strip('\n')
        if status == "active":
            await self.__stop_service(service_name)
        else:
            return True

