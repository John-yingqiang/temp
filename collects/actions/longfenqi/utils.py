import base64
import hashlib
import json
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


def createSign(data, key):
    # 创建md5对象
    data = dictSort(data)
    data = convertDict(data)
    print(data)
    md5key = hashlib.md5(key.encode()).hexdigest()
    md5Str = hashlib.md5((data+md5key).encode()).hexdigest()
    return md5Str


def RSAEncrypt(data, key):
    # 初始化加密器
    return encrypt(json.dumps(data), key)


def RSADecrypt(data, key):
    # 解密方法
    return decrypt(data, key)


def encrypt(data, pubkey):
    pubobj = Cipher_pkcs1_v1_5.new(RSA.importKey(pubkey))
    length = len(data)
    msg = data.encode(encoding="utf-8")
    default_length = 245
    if length < default_length:
        encry_text = base64.b64encode(pubobj.encrypt(msg))  # 通过生成的对象加密message明 # 对传递进来的用户名或密码字符串
        encry_value = encry_text.decode('utf8')
        return encry_value
        # 需要分段
    offset = 0
    res = []
    while length - offset > 0:
        if length - offset > default_length:
            res.append(pubobj.encrypt(msg[offset:offset + default_length]))
        else:
            res.append((pubobj.encrypt(msg[offset:])))
        offset += default_length
    a = b"".join(res)
    return base64.b64encode(a).decode()


def decrypt(data, prikey):
    decodeStr = base64.b64decode(data)
    prikey = Cipher_pkcs1_v1_5.new(RSA.importKey(prikey))
    length = len(decodeStr)
    default_length = 256
    if length <= default_length:
        encry_text = prikey.decrypt(decodeStr, b'rsa')  # 通过生成的对象加密message明 # 对传递进来的用户名或密码字符串
        encry_value = encry_text.decode('utf8')
        return encry_value
        # 需要分段
    offset = 0
    res = []
    byte = []
    while length - offset > 0:
        if length - offset > default_length:
            byte.append(decodeStr[offset:offset + default_length])
        else:
            byte.append(decodeStr[offset:])
        offset += default_length
    for i in byte:
        res.append(prikey.decrypt(i,b'rsa').decode())
    return "".join(res)


def dictSort(data):
    data = sorted(data.items(), key=lambda d: d[0])
    i = 0
    for key in data:
        if isinstance(key[1], dict):
            key1 = list(key)
            value = dictSort(key1[1])
            key1[1] = value
            data[i] = tuple(key1)
        i += 1
    return data


def convertDict(data):
    str1 = ''
    for key in data:
        if key[0] != 'sign':
            if isinstance(key[1], list):
                if str1 == '':
                    if isinstance(key[0], str):
                        str1 += convertDict(key[1])
                    else:
                        str1 += key[0] + convertDict(key[1])
                else:
                    if isinstance(key[0], str):
                        str1 += '&' + key[0] +'='+ convertDict(key[1])
                    else:
                        str1 += '&' + key[0] + '=' + convertDict(key[1])
            else:
                if str1 == '':
                    str1 += str(key[0]) + '=' + str(key[1])
                else:
                    str1 += '&' + str(key[0]) + '=' + str(key[1])
    return str1
