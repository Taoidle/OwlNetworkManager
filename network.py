import subprocess
import os
import json

CONFIG_PATH = "/etc/owl/net-server/wifi_list.json"


def getNetworkStatus():
    network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $1} {print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    network_status = network_status_list[1].decode('utf-8').strip('\n')
    network_connection = network_status_list[2].decode('utf-8').strip('\n')
    if network_status == "connected" and network_connection != "Hotspot":
        return {"statusCode": "200", "ssid": network_connection, "status": "connected"}
    else:
        return {"statusCode": "200",  "status": "disconnected"}


def getNetworkWiFiList():
    json_file = open(CONFIG_PATH, 'r', encoding='utf-8')
    wifi_list = json.load(json_file)
    json_file.close()
    return {"wifi": wifi_list}


def setNetworkWifi(ssid: str, password: str):
    flag = "wifi"
    network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    network_status = network_status_list[0].decode('utf-8').strip('\n')
    network_connection = network_status_list[1].decode('utf-8').strip('\n')
    if network_status == "connected" and network_connection != "Hotspot" and network_connection != "--":
        while not downConnection(network_connection): pass
    if network_status == "connected" and network_connection == "Hotspot":
        while not downHotspot(): pass
        flag = "ap"
    if not connectWifi(ssid, password):
        while not deleteConnection(ssid): pass
        if flag == "ap":
            restartAp()
        else:
            os.system("nmcli dev wifi rescan")
            os.system("nmcli c up " + network_connection)


def downConnection(ssid: str):
    os.system("nmcli c down " + ssid)
    network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    network_status = network_status_list[0].decode('utf-8').strip('\n')
    network_connection = network_status_list[1].decode('utf-8').strip('\n')
    if network_status == "disconnected" and network_connection == "--": return True
    else: return False


def upHotspot():
    os.system("nmcli c up Hotspot")
    network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    network_status = network_status_list[0].decode('utf-8').strip('\n')
    network_connection = network_status_list[1].decode('utf-8').strip('\n')
    if network_status == "connected" and network_connection == "Hotspot": return True
    else: return False


def downHotspot():
    os.system("nmcli c down Hotspot")
    network_status = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3}'", shell=True, stdout=subprocess.PIPE).stdout.readline().decode('utf-8').strip('\n')
    if network_status == "connected": return False
    else: return True


def connectWifi(ssid: str, password: str):
    os.system("nmcli dev wifi rescan")
    os.system("nmcli dev wifi c " + ssid + " password \"" + password + "\"")
    network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    network_status = network_status_list[0].decode('utf-8').strip('\n')
    network_connection = network_status_list[1].decode('utf-8').strip('\n')
    if network_status == "connected" and network_connection != "Hotspot": return True
    else: return False


def restartAp():
    os.system("nmcli dev wifi rescan")
    updateWiFiList()
    while upHotspot(): break


def deleteConnection(ssid: str):
    os.system("nmcli c delete " + ssid)
    check = subprocess.Popen("nmcli c show | grep \"" + ssid + "\"", shell=True, stdout=subprocess.PIPE).stdout.readline().decode('utf-8').strip('\n')
    if check != "": return False
    else: return True


def rescanWiFiList():
    network_status_list = subprocess.Popen("nmcli device status | grep \" wifi \" | awk '{print $3} {print $4}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    network_status = network_status_list[0].decode('utf-8').strip('\n')
    network_connection = network_status_list[1].decode('utf-8').strip('\n')
    if network_status == "connected" and network_connection != "Hotspot":
        updateWiFiList()
        return {"statusCode": "200", "message": "ok"}
    else:
        return {"statusCode": "401", "message": "Ap model can not support WiFi resan"}


def updateWiFiList():
    wifi_info = subprocess.Popen("nmcli dev wifi list | grep Infra | awk '$1!=\"*\" {print $2} {print $7}'", shell=True, stdout=subprocess.PIPE).stdout.readlines()
    wifi_json = {}
    for i, count in zip(range(0, len(wifi_info), 2), range(len(wifi_info) // 2)):
        wifi_json.update({str(count): {"ssid": wifi_info[i].decode('utf-8').strip('\n'), "signal": wifi_info[i + 1].decode('utf-8').strip('\n')}})
    with open(CONFIG_PATH, "w", encoding='utf-8') as f:
        f.write(json.dumps(wifi_json, ensure_ascii=False))
    f.close()


