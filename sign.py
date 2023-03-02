from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
import os
import base64
import zipfile

zipf = zipfile.ZipFile("sign_files/update_unsig.zip", 'w')
pre_len = len(os.path.dirname("./compress/"))
for parent, dirnames, filenames in os.walk("./compress/"):
    for filename in filenames:
        path_file = os.path.join(parent, filename)
        arc_name = path_file[pre_len:].strip(os.path.sep)
        zipf.write(path_file, arc_name)
zipf.close()

rsa_path = ".ssh/id_rsa"

rsa_file = open(rsa_path)
key = rsa_file.read()
rsa_key = RSA.importKey(key.encode("utf-8"))
signer = PKCS1_v1_5.new(rsa_key)
digest = SHA256.new()

file_in = open("./sign_files/update_unsig.zip", "rb+")

file_data = file_in.read()

digest.update(file_data)
sign = signer.sign(digest)
signature = base64.b64encode(sign)

version_file = open("./compress/VERSION", "r")
version = version_file.readline()

file_out = open("./sign_files/update(" + version + ").zip", "wb+")
file_data = signature + file_data

file_out.write(file_data)
version_file.close()
file_out.close()
file_in.close()
rsa_file.close()
