from config import OFFLINE_CONF as conf_path
import json
import subprocess

json_file = open(conf_path, 'r', encoding='utf-8')
conf = json.load(json_file)
json_file.close()

if conf["run"]:
    sub = subprocess.Popen("chmod a+x " + conf["address"] + " && python3 " + conf["address"] + conf["main"], shell=True, stdout=subprocess.PIPE)