import subprocess
import os
import json

CONFIG_PATH = "/etc/owl/net-server/wifi_list.json"


class NetWork:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pass

    def getNetworkStatus(self):
        network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $1} {print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        network_status = network_status_list[1].decode('utf-8').strip('\n')
        network_connection = network_status_list[2].decode('utf-8').strip('\n')
        if network_status == "connected" and network_connection != "Hotspot":
            return {"statusCode": "200", "ssid": network_connection, "status": "connected"}
        else:
            return {"statusCode": "200", "status": "disconnected"}

    def getNetworkWiFiList(self):
        json_file = open(CONFIG_PATH, 'r', encoding='utf-8')
        wifi_list = json.load(json_file)
        json_file.close()
        return {"wifi": wifi_list}

    def setNetworkWifi(self, ssid: str, password: str):
        network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        network_connection = network_status_list[1].decode('utf-8').strip('\n')
        if network_connection == "Hotspot":
            self.__downConnection("Hotspot")
            os.system("nmcli dev wifi rescan")
        if not self.__connectWifi(ssid, password):
            while not self.__deleteConnection(ssid): pass
            if network_connection != "Hotspot":
                os.system("nmcli dev wifi rescan")
                os.system("nmcli c up " + network_connection)

    def __downConnection(self, ssid: str):
        os.system("nmcli c down " + ssid)
        network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        network_status = network_status_list[0].decode('utf-8').strip('\n')
        if network_status == "disconnected":
            return True
        else:
            return False

    def __upHotspot(self):
        os.system("nmcli c up Hotspot")
        network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        network_status = network_status_list[0].decode('utf-8').strip('\n')
        network_connection = network_status_list[1].decode('utf-8').strip('\n')
        if network_status == "connected" and network_connection == "Hotspot":
            return True
        else:
            return False

    def __connectWifi(self, ssid: str, password: str):
        os.system("nmcli dev wifi c \"" + ssid + "\" password \"" + password + "\"")
        network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        network_status = network_status_list[0].decode('utf-8').strip('\n')
        network_connection = network_status_list[1].decode('utf-8').strip('\n')
        if network_status == "connected" and network_connection != "Hotspot":
            return True
        else:
            return False

    def __restartAp(self):
        os.system("nmcli dev wifi rescan")
        self.__updateWiFiList()
        while self.__upHotspot(): break

    def __deleteConnection(self, ssid: str):
        os.system("nmcli c delete " + ssid)
        check = subprocess.Popen("nmcli c show | grep \"" + ssid + "\"", shell=True, stdout=subprocess.PIPE).stdout.readline().decode('utf-8').strip('\n')
        if check != "":
            return False
        else:
            return True

    def rescanWiFiList(self):
        network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        network_status = network_status_list[0].decode('utf-8').strip('\n')
        network_connection = network_status_list[1].decode('utf-8').strip('\n')
        if network_status == "connected" and network_connection == "Hotspot":
            self.__downConnection("Hotspot")
            os.system("nmcli dev wifi rescan")
            self.__updateWiFiList()
        else:
            self.__updateWiFiList()

    def __updateWiFiList(self):
        wifi_info = subprocess.Popen("nmcli dev wifi list | grep Infra | awk '$1!=\"*\"' | awk '{print $2} {print $7}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
        wifi_json = {}
        for i, count in zip(range(0, len(wifi_info), 2), range(len(wifi_info) // 2)):
            wifi_json.update({str(count): {"ssid": wifi_info[i].decode('utf-8').strip('\n'), "signal": wifi_info[i + 1].decode('utf-8').strip('\n')}})
        with open(CONFIG_PATH, "w", encoding='utf-8') as f:
            f.write(json.dumps(wifi_json, ensure_ascii=False))
        f.close()
