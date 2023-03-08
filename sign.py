from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
import os
import base64
import zipfile
import json
import time
import datetime

VERSION_PATH = './compress/VERSION'
KERNEL = "6.1.11"
TAG = "debug"
TARGET_FILE = "sign_files/update_unsig.zip"
SIGN_FILE = "sign_files/update.zip"
DIR_IN = "./compress/"
RSA_PATH = ".ssh/id_rsa"


class Sign:
    _instance = None
    __date = str(datetime.datetime.now()).split(" ")[0].replace('-', '.')[2::]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pass

    def sign(self, rsa_path: str, sign_file: str, target_file: str, version: str = "", compress: bool = False,
             dir_in: str = ""):
        rsa_file = open(rsa_path)
        key = rsa_file.read()
        rsa_key = RSA.importKey(key.encode("utf-8"))
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA256.new()

        if compress and dir_in != "":
            self.__target_dir(target_file, dir_in)

        file_in = open(target_file, "rb+")
        file_data = file_in.read()

        digest.update(file_data)
        sign = signer.sign(digest)
        signature = base64.b64encode(sign)

        if version != "":
            sign_list = sign_file.split(".")
            sign_list[len(sign_list) - 2] = sign_list[len(sign_list) - 2] + f"({version})"
            sign_file = ""
            for i in sign_list:
                sign_file = sign_file + "." + i
            sign_file = sign_file[1::]
        file_out = open(sign_file, "wb+")
        file_data = signature + file_data

        file_out.write(file_data)
        file_out.close()
        file_in.close()
        rsa_file.close()

    def update_version(self, version_path: str, kernel: str, tag: str = "", inc: bool = True) -> str:
        version = self.generate_version(version_path, kernel, tag, inc)
        version_file_r = open(version_path, "r")
        json_data = json.load(version_file_r)
        json_data["version"] = version
        version_file_w = open(version_path, "w")
        json.dump(json_data, version_file_w, ensure_ascii=False)
        version_file_w.close()
        version_file_r.close()
        return version

    def generate_version(self, version_path: str, kernel: str, tag: str = "", inc: bool = True) -> str:
        if os.path.exists(version_path):
            version_file = open(version_path, "r+")
            date_list = json.load(version_file)["version"].split(".")
            date_v = date_list[3] + "." + date_list[4] + "." + date_list[5][0:len(date_list[5]) - 1]
            if date_v == self.__date:
                if inc:
                    suffix = chr(ord(date_list[5][len(date_list[5]) - 1:len(date_list[5])]) + 1)
                else:
                    suffix = chr(ord(date_list[5][len(date_list[5]) - 1:len(date_list[5])]))
                date = date_v + suffix
            else:
                date = self.__date + 'a'
            version_file.close()
        else:
            version_file = open(version_path, "w+")
            json.dump({"version": ""}, version_file)
            version_file.close()
            date = self.__date + 'a'
        hash_hex = self.__get_hash()
        version, version_list = "", [kernel, date, tag, hash_hex]
        for i in version_list:
            if i != "":
                version = version + '.' + i
        version = version[1::]
        return version

    def __target_dir(self, target_file: str, dir_in: str) -> None:
        zipf = zipfile.ZipFile(target_file, 'w')
        pre_len = len(os.path.dirname(dir_in))
        for parent, dirnames, filenames in os.walk(dir_in):
            for filename in filenames:
                path_file = os.path.join(parent, filename)
                arc_name = path_file[pre_len:].strip(os.path.sep)
                zipf.write(path_file, arc_name)
        zipf.close()

    def __get_hash(self) -> str:
        digest = SHA256.new()
        digest.update(str(time.time_ns()).encode("utf-8"))
        return digest.hexdigest()[::8]


if __name__ == '__main__':
    sign_version = Sign().update_version(VERSION_PATH, KERNEL)
    Sign().sign(RSA_PATH, SIGN_FILE, TARGET_FILE, sign_version, True, DIR_IN)
