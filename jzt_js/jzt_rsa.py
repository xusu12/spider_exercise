from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
import base64

# 公钥
public_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCK0GF/A3P7a1PNPh9ZNcprFnFUi/2w2C97vCFxyCgggtcT3BpCV8Yc32HWYR3a2Gtk1LF456ZB4kI9EbxJMl3bnK9esD/cQ1TD1YoPmey5S6UaVgO1IKGDx2OomvLUfbRMmTOUtttCogD9ps3knL15DvfhXiaAjMML8Ck8bDPXZQIDAQAB
-----END PUBLIC KEY-----'''

def rsa_encrypt(message):
    """校验RSA加密 使用公钥进行加密"""
    cipher = Cipher_pkcs1_v1_5.new(RSA.importKey(public_key))
    cipher_text = base64.b64encode(cipher.encrypt(message.encode())).decode()
    return cipher_text

res = rsa_encrypt('1601370706338')
print(res)