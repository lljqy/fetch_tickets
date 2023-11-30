import json
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def extract(t):
    h = "0123456789ABCDEF".encode('utf-8')
    e = base64.b64decode(t)
    n = e
    f = "Dt8j9wGw%6HbxfFn".encode('utf-8')
    a = None
    try:
        cipher = AES.new(f, AES.MODE_CBC, h)
        a = unpad(cipher.decrypt(n), AES.block_size)
        r = a.decode('utf-8')
        return json.loads(r)
    except Exception as e:
        print(e)
        f = "jo8j9wGw%6HbxfFn".encode("utf-8")
        cipher = AES.new(f, AES.MODE_CBC, h)
        a = unpad(cipher.decrypt(n), AES.block_size)
        r = a.decode('utf-8')
        return json.loads(r)


if __name__ == '__main__':
    data = "95780ba0943730051dccb5fe3918f9fe0b265875366ec51d2bbc4ecc85d8dc5a51890bb92ed7e87c2f1058839c9031ce82e2953071eef9336e5311c9470ee19f28191d49fa180a52c2f725536bc769427f2ddca3157d0559a947b42f661af659206102689ec47f28ba74b6209a9f2e2f"
    # password = b'1234567812345678'  # 秘钥，b就是表示为bytes类型
    # iv = b'1234567812345678'  # iv偏移量，bytes类型
    # text = b'abcdefghijklmnhi'  # 需要加密的内容，bytes类型
    # aes = AES.new(password, AES.MODE_CBC, iv)  # 创建一个aes对象
    # # AES.MODE_CBC 表示模式是CBC模式
    # en_text = aes.encrypt(text)
    # print("密文：", en_text)  # 加密明文，bytes类型
    # iv = "0123456789ABCDEF".encode('utf-8')
    # aes = AES.new("Dt8j9wGw%6HbxfFn".encode('utf-8'), AES.MODE_CBC, iv)  # CBC模式下解密需要重新创建一个aes对象
    #
    # den_text = aes.decrypt(data)
    # print("明文：", den_text.decode('utf-8'))
    print(extract(data))
