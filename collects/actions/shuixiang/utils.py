#coding=utf-8
import json
from Crypto.Cipher import AES
import base64
import requests

# for test
app_id = "HFKFHKH423412KLK"
aeskey = 'AmCILBEADCgkHhDK'


class AESENCRYPT(object):
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_ECB

    def padding(self, text):
        text = text.encode("utf-8")
        length = 16
        count = len(text)

        if (count <= length):
            add = length - count
        elif count > length:
            add = length - (count % length)

        text1 = text + (chr(add) * add).encode('utf-8')

        return text1

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode)
        padding_result = self.padding(text)

        self.ciphertext = cryptor.encrypt(padding_result)
        cryptedStr = str(base64.b64encode(self.ciphertext), encoding='utf-8')

        return cryptedStr

    def decrypt(self, text):
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        base_text = base64.b64decode(text)
        cryptor = AES.new(self.key, self.mode)
        decode_text = cryptor.decrypt(base_text)

        return unpad(decode_text.decode('utf-8'))

def send_api(data, url="http://106.15.126.217:8092/beadwalletloanapp/sxyDrainage/jqks/checkUser.do"):
    headers = {"Content-Type": "application/json;charset=utf-8"}
    response = requests.post(url, data, headers=headers)
    print("result:", response.text)


if __name__ == "__main__":
    test_dict = {"idCard":"421127199510211517","name":"王子杰","phone":"15727150000"}

    test_encrypt = AESENCRYPT(aeskey)
    encontent = test_encrypt.encrypt(json.dumps(test_dict, ensure_ascii=False, separators=(',',':')))

    test_data = {"appId":"HFKFHKH423412KLK", "request":encontent}
    json_result = json.dumps(test_data)
    print("json:", json_result)

    send_api(json_result)