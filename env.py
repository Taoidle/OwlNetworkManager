from sql import Sqlite
import subprocess
from fastapi import File


class Env:
    _instance = None
    _sql = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls._sql = Sqlite()
        return cls._instance

    def __int__(self):
        pass

    async def getEnvListPython(self, offset: int, limit: int):
        return await self.getEnvList("python", offset, limit)

    async def getEnvListCpp(self, offset: int, limit: int):
        return await self.getEnvList("cpp", offset, limit)

    async def getEnvListOsPkg(self, offset: int, limit: int):
        return await self.getEnvList("pkg", offset, limit)

    async def getEnvList(self, tag: str, offset: int, limit: int):
        data = []
        sql_str = "SELECT PACKAGE, VERSION from ENV WHERE TAG='" + tag + "' ORDER BY LOWER(PACKAGE) ASC LIMIT " + str(
            offset * limit) + "," + str(limit)
        for item in self._sql.cursor.execute(sql_str):
            data.append({"package": item[0], "version": item[1]})
        print("data: ", data)
        sql_str = "SELECT count(*) FROM ENV WHERE TAG='" + tag + "'"
        total = self._sql.cursor.execute(sql_str).fetchall()[0][0]
        return {"total": total, "data": data}

    async def envReloadPython(self):
        pip_list = subprocess.Popen("pip list | awk '{print $1} {print $2}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        pip_list = pip_list[4::]
        package_total = len(pip_list) // 2
        if self._sql.cursor.execute('''SELECT count(*) FROM ENV WHERE TAG="python"''').fetchall()[0][0] == 0:
            self._sql.cursor.execute(
                "INSERT INTO ENV (PACKAGE, VERSION, TAG) VALUES ('opencv-contrib-python','4.5.4','python')")
            self._sql.conn.commit()
        for i in range(package_total):
            package_name = pip_list[2 * i].decode('utf-8').strip('\n')
            package_version = pip_list[2 * i + 1].decode('utf-8').strip('\n')
            # print("package_name: ", package_name, " package_version: ", package_version)
            self._sql.cursor.execute("REPLACE INTO ENV (PACKAGE, VERSION, TAG) VALUES (?,?,'python')",
                                     (package_name, package_version))
        self._sql.conn.commit()
        return {"statusCode": "200", "status": "success"}

    async def envReloadCpp(self):
        if self._sql.cursor.execute('''SELECT count(*) FROM ENV WHERE TAG="cpp"''').fetchall()[0][0] == 0:
            self._sql.cursor.execute("INSERT INTO ENV (PACKAGE, VERSION, TAG) VALUES ('apriltag3','3.2.0 - 1','cpp')")
            self._sql.cursor.execute("INSERT INTO ENV (PACKAGE, VERSION, TAG) VALUES ('boost','1_81_0','cpp')")
            self._sql.cursor.execute("INSERT INTO ENV (PACKAGE, VERSION, TAG) VALUES ('OpenCV','4.5.4','cpp')")
            self._sql.cursor.execute("INSERT INTO ENV (PACKAGE, VERSION, TAG) VALUES ('protobuf','V21.11','cpp')")

            self._sql.conn.commit()
        return {"statusCode": "200", "status": "success"}

    async def envReloadPkg(self):
        pkg_list = subprocess.Popen("dpkg-query -l | cat | awk '{print $2} {print $3}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        pkg_list = pkg_list[10::]
        package_total = len(pkg_list) // 2
        for i in range(package_total):
            package_name = pkg_list[2 * i].decode('utf-8').strip('\n')
            package_version = pkg_list[2 * i + 1].decode('utf-8').strip('\n')
            self._sql.cursor.execute("REPLACE INTO ENV (PACKAGE, VERSION, TAG) VALUES (?,?,'pkg')",
                                     (package_name, package_version))
        self._sql.conn.commit()
        return {"statusCode": "200", "status": "success"}

    async def saveUpload(self, file: File):
        file_data = await file.read()
