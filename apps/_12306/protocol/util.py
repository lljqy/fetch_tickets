import base64
import requests

from retry import retry

UINT8_BLOCK = 16


class Session(requests.Session):

    @retry(tries=3, delay=5)
    def get(self, url: str, **kwargs):
        kwargs.setdefault("verify", False)
        self.cookies.update(self.headers)
        response = super().get(url, **kwargs)
        cookies_dict = response.cookies.get_dict()
        if cookies_dict:
            self.cookies.update(cookies_dict)
        return response

    @retry(tries=3, delay=5)
    def post(self, url: str, **kwargs):
        kwargs.setdefault("verify", False)
        self.cookies.update(self.headers)
        response = super().post(url, **kwargs)
        cookies_dict = response.cookies.get_dict()
        if cookies_dict:
            self.cookies.update(cookies_dict)
        return response


def generate_unicode_url_encoded_string(city: str) -> str:
    # 将城市名称转换为Unicode编码的URL编码形式
    unicode_encoded_city = ''.join(['%04x' % ord(c) for c in city])
    # 生成最终的字符串
    return '%u' + '%u'.join(
        unicode_encoded_city[index:index + 4] for index in range(0, len(unicode_encoded_city), 4))


class Encrypt:
    @staticmethod
    def _unsigned_right_shift(num: int, shift: int) -> int:
        # 先转换为正数
        positive_num = num + (1 << 32) if num < 0 else num
        # 右移
        shifted = positive_num >> shift
        # 转换回32位无符号整数
        return (shifted - (1 << 31)) if shifted > (1 << 31) - 1 else shifted

    @staticmethod
    def _js_bit_xor(a: int, b: int) -> int:
        bit_limit = 32
        bit_length_a, bit_length_b = a.bit_length(), b.bit_length()
        value = a ^ b
        if bit_length_a < bit_limit and bit_length_b < bit_limit:
            return value
        compensate_code = format(value, "064b")
        coe = 1 if value > 0 else -1
        bit_code = compensate_code[-32:]
        if bit_code[0] == "0":
            return int(bit_code, base=2) * coe
        bit_code = "".join(["0" if bit == "1" else "1" for bit in bit_code])
        return -(int(bit_code, base=2) + 1) * coe

    @staticmethod
    def _js_right_bit(num: int, steps: int) -> int:
        if num > 0:
            compensate_code = format(num, "032b")
        else:
            bit_code = format(-num, "032b")
            reversed_bit_code = "".join(["0" if bit == "1" else "1" for bit in bit_code])
            reversed_compensate_value = int(reversed_bit_code, base=2)
            reversed_compensate_value += 1
            bit_code = format(reversed_compensate_value, "032b")
            compensate_code = "1" + bit_code[1:]
        code = (compensate_code + "0" * steps)[-32:]
        if code[0] == "0":
            return int(code, base=2)
        code = "".join(["0" if bit == "1" else "1" for bit in code])
        return -(int(code, base=2) + 1)

    @staticmethod
    def _padding(original_buffer: list[int]) -> list[int]:
        if not original_buffer:
            return list()

        padding_length = 16 - len(original_buffer) % UINT8_BLOCK
        original_buffer.extend([padding_length] * padding_length)
        padded_buffer = original_buffer
        return padded_buffer

    def _tau_transform(self, a: int) -> int:
        s_box = [214, 144, 233, 254, 204, 225, 61, 183, 22, 182, 20, 194, 40, 251, 44, 5, 43, 103, 154, 118, 42, 190, 4,
                 195,
                 170, 68, 19, 38, 73, 134, 6, 153, 156, 66, 80, 244, 145, 239, 152, 122, 51, 84, 11, 67, 237, 207, 172,
                 98, 228,
                 179, 28, 169, 201, 8, 232, 149, 128, 223, 148, 250, 117, 143, 63, 166, 71, 7, 167, 252, 243, 115, 23,
                 186, 131,
                 89, 60, 25, 230, 133, 79, 168, 104, 107, 129, 178, 113, 100, 218, 139, 248, 235, 15, 75, 112, 86, 157,
                 53, 30,
                 36, 14, 94, 99, 88, 209, 162, 37, 34, 124, 59, 1, 33, 120, 135, 212, 0, 70, 87, 159, 211, 39, 82, 76,
                 54, 2,
                 231, 160, 196, 200, 158, 234, 191, 138, 210, 64, 199, 56, 181, 163, 247, 242, 206, 249, 97, 21, 161,
                 224, 174,
                 93, 164, 155, 52, 26, 85, 173, 147, 50, 48, 245, 140, 177, 227, 29, 246, 226, 46, 130, 102, 202, 96,
                 192, 41,
                 35, 171, 13, 83, 78, 111, 213, 219, 55, 69, 222, 253, 142, 47, 3, 255, 106, 114, 109, 108, 91, 81, 141,
                 27,
                 175, 146, 187, 221, 188, 127, 17, 217, 92, 65, 31, 16, 90, 216, 10, 193, 49, 136, 165, 205, 123, 189,
                 45, 116,
                 208, 18, 184, 229, 180, 176, 137, 105, 151, 74, 12, 150, 119, 126, 101, 185, 241, 9, 197, 110, 198,
                 132, 24,
                 240, 125, 236, 58, 220, 77, 32, 121, 238, 95, 62, 215, 203, 57, 72]
        return (self._js_right_bit(s_box[a >> 24 & 0xff], 24) | self._js_right_bit(s_box[a >> 16 & 0xff], 16)
                | self._js_right_bit(s_box[a >> 8 & 0xff], 8) | s_box[a & 0xff])

    def _rotate_left(self, x: int, y: int) -> int:
        return self._js_right_bit(x, y) | self._unsigned_right_shift(x, 32 - y)

    def _t_transform1(self, a: int) -> int:
        b = self._tau_transform(a)
        ans = b
        for y in (2, 10, 18, 24):
            ans = self._js_bit_xor(ans, self._rotate_left(b, y))
        return ans

    def _t_transform2(self, a: int) -> int:
        b = self._tau_transform(a)
        ans = b
        for y in (13, 23):
            ans = self._js_bit_xor(ans, self._rotate_left(b, y))
        return ans

    def _encrypt_round_keys(self, key: list[int]) -> list[int]:
        keys = list()
        mk = [self._js_right_bit(key[0], 24) | self._js_right_bit(key[1], 16) |
              self._js_right_bit(key[2], 8) | key[3],
              self._js_right_bit(key[4], 24) | self._js_right_bit(key[5], 16) |
              self._js_right_bit(key[6], 8) | key[7],
              self._js_right_bit(key[8], 24) | self._js_right_bit(key[9], 16) |
              self._js_right_bit(key[10], 8) | key[11],
              self._js_right_bit(key[12], 24) | self._js_right_bit(key[13], 16) |
              self._js_right_bit(key[14], 8) | key[15]]
        before, after = 4, 32
        k = [0] * (before + after)
        fk = [2746333894, 1453994832, 1736282519, 2993693404]
        ck = [462357, 472066609, 943670861, 1415275113, 1886879365, 2358483617, 2830087869, 3301692121, 3773296373,
              4228057617, 404694573, 876298825, 1347903077, 1819507329, 2291111581, 2762715833, 3234320085, 3705924337,
              4177462797, 337322537, 808926789, 1280531041, 1752135293, 2223739545, 2695343797, 3166948049, 3638552301,
              4110090761, 269950501, 741554753, 1213159005, 1684763257]
        for index in range(before):
            # k[index] = self._py_num_to_js_num(mk[index] ^ fk[index])
            k[index] = self._js_bit_xor(mk[index], fk[index])
        for index in range(after):
            params = 0
            for value in (k[index + 1], k[index + 2], k[index + 3], ck[index]):
                params = self._js_bit_xor(params, value)
            k[index + 4] = self._js_bit_xor(k[index], self._t_transform2(params))
            keys.append(k[index + 4])
        return keys

    def _get_chain_block(self, arr: list[int], base_index: int = 0) -> list[int]:
        return [self._js_right_bit(arr[base_index], 24) | self._js_right_bit(arr[base_index + 1], 16) |
                self._js_right_bit(arr[base_index + 2], 8) | arr[base_index + 3],
                self._js_right_bit(arr[base_index + 4], 24) | self._js_right_bit(arr[base_index + 5], 16) |
                self._js_right_bit(arr[base_index + 6], 8) | arr[base_index + 7],
                self._js_right_bit(arr[base_index + 8], 24) | self._js_right_bit(arr[base_index + 9], 16) |
                self._js_right_bit(arr[base_index + 10], 8) | arr[base_index + 11],
                self._js_right_bit(arr[base_index + 12], 24) | self._js_right_bit(arr[base_index + 13], 16) |
                self._js_right_bit(arr[base_index + 14], 8) | arr[base_index + 15]]

    def _do_block_crypt(self, block_data: list[int], round_keys: list[int]) -> list[int]:
        x_block = [0] * 36
        for index, val in enumerate(block_data):
            x_block[index] = val
        for index in range(32):
            params = 0
            for value in (x_block[index + 1], x_block[index + 2], x_block[index + 3], round_keys[index]):
                params = self._js_bit_xor(params, value)
            x_block[index + 4] = self._js_bit_xor(x_block[index], self._t_transform1(params))
        y_block = [x_block[35], x_block[34], x_block[33], x_block[32]]
        return y_block

    def encrypt_password(self, password: str, key: str = "tiekeyuankp12306", mode: str = "base64") -> str:
        key_array = list(map(lambda x: ord(x), key))
        encrypt_round_keys = self._encrypt_round_keys(key_array)
        plain_byte_array = list(map(lambda x: ord(x), password))
        padded = self._padding(plain_byte_array)
        block_times = (len(padded) + UINT8_BLOCK - 1) // UINT8_BLOCK
        out_array = list()
        for index in range(block_times):
            round_index = index * UINT8_BLOCK
            block = self._get_chain_block(padded, round_index)
            cipher_block = self._do_block_crypt(block, encrypt_round_keys)
            for bit in range(UINT8_BLOCK):
                out_array.append(cipher_block[int(bit / 4)] >> (3 - bit) % 4 * 8 & 0xff)
        if mode == "base64":
            byte_array = bytearray(out_array)
            return "@" + base64.b64encode(byte_array).decode("utf-8")
        return "@" + "".join(map(lambda x: chr(x), out_array))

    def get_encrypt_data(self) -> str:
        """
        加密"otn/confirmPassenger/confirmSingleForQueue"中的encryptData参数，难度比较大，后面再实现
        :return:
        """
        pass
