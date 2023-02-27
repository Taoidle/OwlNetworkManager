from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
import base64

rsa_path = ""

rsa_file = open(rsa_path)
key = rsa_file.read()
rsa_key = RSA.importKey(key.encode("utf-8"))
signer = PKCS1_v1_5.new(rsa_key)
digest = SHA256.new()

file_in = open("", "rb+")

file_data = file_in.read()


digest.update(file_data)
sign = signer.sign(digest)
signature = base64.b64encode(sign)


file_out = open("", "wb+")
file_data = signature + file_data
file_out.write(file_data)
file_out.close()

file_in.close()
rsa_file.close()
