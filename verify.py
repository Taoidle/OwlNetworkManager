from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
import base64

rsa_pub_file = open(".ssh/id_rsa.pub", encoding="gbk")
key = rsa_pub_file.read()
rsakey = RSA.importKey(key.encode("utf-8"))
verifier = PKCS1_v1_5.new(rsakey)
digest = SHA256.new()

file_in = open("./sign_files/update(6.1.11.23.08.03b.debug.fff21822).zip", "rb+")
# print(file_in.read())

# signature_file = open("./files/CMakeLists.zip.sig", "rb+")
# signature = signature_file.read()
# print(signature)
# print(signature.decode("utf-8"))
# print(signature + file_in.read())

# Assumes the data is base64 encoded to begin with
file_data = file_in.read()
# new_data = signature.encode("utf-8") + file_data
# print(len(file_data))
print(file_data[0:512])
digest.update(file_data[512::])
# print(digest)
is_verify = verifier.verify(digest, base64.b64decode(file_data[0:512]))
print(is_verify)

file_out = open("./sign_files/verify.zip", "wb+")
file_out.write(file_data[512::])
file_out.close()

# signature_file.close()
file_in.close()
rsa_pub_file.close()