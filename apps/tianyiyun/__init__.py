import base64

special_str = '53\x1e\x93ª)\xadó'
base64_encoded = base64.b64encode(special_str.encode()  + b'\x00').decode()
print(base64_encoded)
