import re
import json
import time
import base64
import urllib
from pathlib import Path
from datetime import datetime
from operator import itemgetter
from urllib.parse import urljoin, urlencode

import requests
import pandas as pd
from retry import retry
from fake_useragent import UserAgent
from requests import utils as request_utils
from requests.cookies import RequestsCookieJar

from utils.common import BASE_DIR, time_print
from apps._12306.constants import TICKET_MAP, SEAT_MAP, SITE_MAP

UINT8_BLOCK = 16
SITE_MAP_REVERSE = {site_en_name: site_cn_name for site_cn_name, site_en_name in SITE_MAP.items()}


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


class QuickSpider:
    _SUCCESS = 0
    _FAIL = 1

    def __init__(self) -> None:
        self._encrypt = Encrypt()
        self._base_url = "https://kyfw.12306.cn"
        self._session = Session()
        self._load_cookies()

    def _save_cookies(self) -> None:
        cookies = request_utils.dict_from_cookiejar(self._session.cookies)
        cookies_dir = Path(BASE_DIR) / "apps" / "_12306" / "preserve"
        cookies_dir.mkdir(exist_ok=True)
        cookie_file_path = cookies_dir / "cookies.txt"
        with open(cookie_file_path, "w") as f:
            json.dump(cookies, f)

    def _load_cookies(self) -> None:
        cookies_dir = Path(BASE_DIR) / "apps" / "_12306" / "preserve"
        cookies_dir.mkdir(exist_ok=True)
        cookie_file_path = cookies_dir / "cookies.txt"
        if not cookie_file_path.exists():
            cookie_file_path.touch(exist_ok=True)
            return
        jar = RequestsCookieJar()
        try:
            with open(cookie_file_path, "r") as f:
                cookies = json.load(f)
                for name, value in cookies.items():
                    jar.set(name, value)
            self._session.cookies = jar
        except json.decoder.JSONDecodeError as _:
            time_print("cookie文件有误，重新登陆获取cookie")

    def _get_sms_code(self, user_name: str, cast_num: str, headers: dict[str, str]) -> str:
        """
        :param user_name: 登录用户名
        :param cast_num:  身份证后四位
        :return:
        """
        data = {
            "appid": "otn",
            "username": user_name,
            "castNum": cast_num
        }
        self._session.post(url=urljoin(self._base_url, "passport/web/getMessageCode"), headers=headers, data=data,
                           verify=False)
        sms_code = input("请输入手机验证码")
        return sms_code

    def _check(self, user_name: str, headers: dict[str, str]) -> None:
        data = {"appid": "otn", "username": user_name}
        self._session.post(
            url=urljoin(self._base_url, "passport/web/checkLoginVerify"), headers=headers, data=data, verify=False)

    def _login(self, user_name: str, password: str, cast_num: str, headers: dict[str, str]) -> None:
        self._check(user_name, headers)
        # 1. 获取验证码
        sms_code = self._get_sms_code(user_name, cast_num, headers)
        # {
        # 	"result_message": "登录成功",
        # 	"uamtk": "cCuKQKnUcxB37xtQzk5Ws6Gh8EFVxuzJ5HLe-Qozl1l0",
        # 	"result_code": 0
        # }
        while True:
            # 2. 登录获取cookie
            data = {
                'sessionId': '',
                'sig': '',
                'if_check_slide_passcode_token': '',
                'scene': '',
                'checkMode': '0',
                'randCode': sms_code,
                'username': user_name,
                'password': self._encrypt.encrypt_password(password),
                'appid': 'otn',
            }
            response = self._session.post(url=urljoin(self._base_url, "passport/web/login"), headers=headers, data=data,
                                          verify=False)
            if response.json().get("result_code") != self._SUCCESS:
                sms_code = input("请输入手机验证码")
            else:
                break
        self._session.get(url=urljoin(self._base_url, "otn/login/userLogin"), headers=headers, verify=False)
        self._session.get(url=urljoin(self._base_url, "otn/passport?redirect=/otn/login/userLogin"), headers=headers,
                          verify=False)
        request_utils.add_dict_to_cookiejar(self._session.cookies, cookie_dict={"uamtk": response.json().get("uamtk")})
        # {
        # 	"apptk": null,
        # 	"result_message": "验证通过",
        # 	"result_code": 0,
        # 	"newapptk": "B6P-HFaDHdzCH7wNPpJLDv0hNjb9pwIUfLPaVg09l1l0"
        # }
        response = self._session.post(
            url=urljoin(self._base_url, "passport/web/auth/uamtk"), headers=headers, data={'appid': 'otn'},
            verify=False)

        # {
        # 	"result_code": 0,
        # 	"result_message": "验证通过",
        # 	"username": "刘伦杰",
        # 	"apptk": "B6P-HFaDHdzCH7wNPpJLDv0hNjb9pwIUfLPaVg09l1l0"}
        data = {'tk': response.json().get("newapptk")}
        self._session.post(url=urljoin(self._base_url, "otn/uamauthclient"), headers=headers, data=data, verify=False)
        self._session.get(url=urljoin(self._base_url, "otn/login/userLogin"), headers=headers, verify=False)
        # {
        # 	"validateMessagesShowId": "_validatorMessage",
        # 	"status": true,
        # 	"httpstatus": 200,
        # 	"data": {
        # 		"is_open_updateHBTime": "Y",
        # 		"isstudentDate": false,
        # 		"is_message_passCode": "N",
        # 		"born_date": "1992-09-30",
        # 		"is_phone_check": "N",
        # 		"ei_email": "78*****52@qq.com",
        # 		"studentDate": ["2020-04-01", "2020-11-30", "2020-12-01", "2020-12-31", "2021-01-01", "2025-09-30"],
        # 		"is_uam_login": "Y",
        # 		"is_login_passCode": "Y",
        # 		"user_name": "lxpztgllj",
        # 		"is_sweep_login": "Y",
        # 		"queryUrl": "leftTicket/queryG",
        # 		"nowStr": "20240419223341",
        # 		"psr_qr_code_result": "N",
        # 		"now": 1713537221090,
        # 		"name": "刘伦杰",
        # 		"login_url": "resources/login.html",
        # 		"stu_control": 15,
        # 		"is_login": "Y",
        # 		"is_olympicLogin": "N",
        # 		"other_control": 15
        # 	},
        # 	"messages": [],
        # 	"validateMessages": {}
        # }
        self._session.post(url=urljoin(self._base_url, "otn/login/conf"), headers=headers, verify=False)
        # {
        # 	"validateMessagesShowId": "_validatorMessage",
        # 	"status": true,
        # 	"httpstatus": 200,
        # 	"data": {
        # 		"notify_way": "6",
        # 		"if_show_ali_qr_code": false,
        # 		"isSuperUser": "N",
        # 		"_email": "78*****52@qq.com",
        # 		"user_status": "1",
        # 		"_is_needModifyPassword": null,
        # 		"needEdit": false,
        # 		"member_status": "2",
        # 		"control_code": null,
        # 		"id_type_code": "1",
        # 		"user_name": "刘伦杰",
        # 		"member_level": "2",
        # 		"isCanRegistMember": false,
        # 		"user_regard": "先生,下午好！",
        # 		"resetMemberPwd": "N",
        # 		"_is_active": "Y"
        # 	},
        # 	"messages": [],
        # 	"validateMessages": {}
        # }
        self._session.post(url=urljoin(self._base_url, "otn/index/initMy12306Api"), headers=headers,
                           verify=False)
        self._save_cookies()

    def _query_left_tickets(
            self,
            from_: str,
            to: str,
            start_date: str,
            headers: dict[str, str],
            purpose_code: str = "ADULT"
    ) -> pd.DataFrame:
        if from_ not in SITE_MAP or to not in SITE_MAP:
            raise ValueError(f"‘出发地’({from_})或者‘目的地’({to})有误")
        params = {
            "leftTicketDTO.train_date": start_date,
            "leftTicketDTO.from_station": SITE_MAP.get(from_),
            "leftTicketDTO.to_station": SITE_MAP.get(to),
            "purpose_codes": purpose_code,
        }
        response = self._session.get(
            url=urljoin(self._base_url, "otn/leftTicket/queryG"),
            params=params,
            headers=headers,
            verify=False
        )
        r = response.json()
        if r.get("httpstatus") != requests.status_codes.codes.ok:
            raise RuntimeError("无法查询车次信息")
        results = r.get("data", dict()).get("result", list())
        columns = [
            "secret_str",
            "button_text_info",
            "train_no",
            "train_code",
            "start_station_telecode",
            "end_station_telecode",
            "from_station_telecode",
            "to_station_telecode",
            "start_time",
            "arrive_time",
            "time_consuming",
            "can_web_by",
            "yp_info",
            "start_train_date",
            "train_seat_feature",
            "location_code",
            "from_station_no",
            "to_station_no",
            "is_support_card",
            "controlled_train_flag",
            "gg_num",
            "gr_num",
            "qt_num",
            "rw_num",
            "rz_num",
            "tz_num",
            "wz_num",
            "yb_num",
            "yw_num",
            "yz_num",
            "ze_num",
            "zy_num",
            "swz_num",
            "srrb_num",
            "yp_ex",
            "seat_types",
            "exchange_train_flag",
            "houbu_train_flag",
            "houbu_seat_limit",
            "yp_info_new",
            "dw_flag",
            "stop_check_time",
            "country_flag",
            "local_arrive_time",
            "local_start_time",
            "bed_level_info",
            "seat_discount_info",
            "sale_time"
        ]
        filter_data_rule = itemgetter(*[*list(range(40)), 46, *list(range(48, 52)), *list(range(53, 56))])
        data = [filter_data_rule(result.split("|")) for result in results]
        df = pd.DataFrame(data=data, columns=columns)
        df["from_station_name"] = df["from_station_telecode"].map(SITE_MAP_REVERSE)
        df["to_station_name"] = df["to_station_telecode"].map(SITE_MAP_REVERSE)
        return df[df["can_web_by"] == "Y"]

    def _choose_train(self, headers: dict[str, str], from_: str, to: str, train_info: dict[str, str]) -> None:
        # 检查用户信息
        self._session.post(urljoin(self._base_url, "otn/login/checkUser"), headers=headers, data={'_json_att': ''})
        # 选择车次对应页面提交预订按钮
        date_fmt = "%Y-%m-%d"
        params = {
            "secretStr": train_info.get("secret_str"),
            "train_date": pd.to_datetime(train_info.get("start_train_date")).strftime(date_fmt),
            "back_train_date": datetime.now().strftime(date_fmt),
            "tour_flag": "dc",
            "purpose_codes": train_info.get("purpose_codes"),
            "query_from_station_name": from_,
            "query_to_station_name": to,
            "bed_level_info": train_info.get("bed_level_info"),
            "seat_discount_info": ""
        }
        data = self._params_to_query_data(params) + "&undefined"
        self._session.post(urljoin(self._base_url, "otn/leftTicket/submitOrderRequest"), headers=headers, data=data)

    def _submit(self, start_date: str, headers: dict[str, str], train_info: dict[str, str]) -> None:
        selected_passengers = ["吴炀"]
        seat_type, ticket_type = "二等座", "成人票"
        encrypt_data = """AZ.lhO3nwVHg5PsQEwDf.La6uPxtR4NPAZCi9zdn00YJkprW2S0XI58_tJvP7YstTO3LHXY6Ae0AIhS33SVJifJKfIBmzD
        9WqTRfqI7TNoGqH81_WYdEqNiBpZzDYCNTHJkjxU.2jevk8e96CFt8hbdmqPLVfXfYgvXOp_8NOu_I7W_DEHg2nWj2Wvognd8M5vTW7hlSuCv.Np
        eLZCn_j5CnHijErbtKP.fX5ZTeLXRjNLUwvEBPNqbBnEBS3cL16crrgVQtnQBJiKMsvwyv6Pdas.SbNniyDemz4JqLQ7ju8lI8RnEqFFJmOY9P6y
        zk2nd1oy4w5v4jXnz_pfJ7jxDX_rmR0LGhfho8O.vn6rleKYbeGhv.ej_4HgPi.I0lIKHqC2.jmagd55tzaaaumgtVNLuHS8O7b7yoYuMA5OVTKn
        P3bWyBtHDXoj3HRDxrUymRv9pcVW7ZQK6jgdgpJgBrp8ewlPua2QYByKFMCCax1ihD2wGUE95UPKnFSkQ7jUadtmLTtSiPmvkx6BRyF2SIz_NEQ3
        7cAXS9XkupCO7.U5z6uYNsuf5LGfN1p8Wtf_i.xLa3cCqxvOOrDwohV3OunfSrnOkZQm.Fm3CILyoqKZPc4tm3kqd8njBy8VIJrBHdhf_tIFsqum
        yUc_SO6wPRpbO5Tfe6FbwTrpwiS6LnVpapNBJHqF7_cNdu70Ifv8FZaS3rMPyb0b_tmMor0cVn65z8ATyLhDet0_2YW5uupwZ87agukR9BSkiZx5
        QczNyG2ozLqRQbA3czySwdGKS50HK8Q.ubxAORCJcoF604SWn8hHXUU6Uq7_8SyQzZ0jkYlYcMlR2LgRUxZ7oDLkC7h1RFSA96XJWNri50ZChS0S
        8l0kC9eR1VWhOdC_0SZ5jn8U2nqBxX9VXsQjmz3u861bZGCz3La6jPJqt_R1tELHD_1JP1Y_.w9vEVZKr1Nufu_bwX9PataOyvdgqGVAA053QUq3
        I9DOCn548D46wrHUX6KhlQ1iUDSFF29oXZ2FDeoAIKI3SwB.JdpoNN_h6GVlqsRXACx4ElkNOLDhsfjFVaN8yAAyg_IJQA3t7RWoQLRDTDb7jH1n
        M2PJ80uJf0xCXUBYHCH8o9K0fXckRzFmIS2eLYcFFhoUt28DLo4qjmm3kEJYFIj_XVyWvhXvhWMBJQCgyoPVFrgmRrnoWPhA84lJTKAnfg.FtFmW
        X0tro.d2j0zyD8DAWO_YdYUDgvxe4oWfjZmbhsY4HF2QnJuzzVFiyaoTRr1M9uKjYeL3D3t4bVHIkzZsnz_jxZbtMCGZW2zqZpe9tD.DUH6mo39W
        J.hPyKcZPHTWPyovTtKy6TFIZziM6tBZzTtKL8G54bUiNMYcMmGIZ.cX3CuOsyJvfVi0r3UoFQdyx4Nd1wDIj.Ent.xHkaipwTZgAZxtD4LC_JpM
        JDSoQeL2gIY9nHosS0om3Ngdv77U7YP3frBccXrhGQDx4.RKgi3gfeuTjeB15TlnZfK4k_u1XwYQ4ZP4jXQHllzqJeokrq4Krv.AsAUR2sIUiH3Q
        0b8KDsjxQQLKuhD.AHGi9vQEPRSV2bXRzqOHWw8sh2aMqbTAdDpv5i6gyXj997W_4TfHwcdBEmR1BqNafRh_zokXgOX9WkJEw3tCVT4sK9yl7UxP
        xtYcpLAwStLZXhnyUkqVgP9MxQVJ07cRg82Jw3FnFzfg..U5freUxyHcwnw4w1eZI.H1EpxM0u8AklKsqooNCI79_EOhCWWnlLt7xrEm2_hL20.X
        Xc5y4LX3KTr4XEa2rXeUlzVjlLrbjtjj0A68pzQGDFbR4wubctys7pkcIXE2ZgLi83PovjSN7tvPbuVCiBLbqEfb3eW7M6SgACOmsUeUgRWpHV1t
        1.PeQHmYc9o_3EyN2qG9sUox2BIH5HE4uONrfTdBa4ZQGApBqmnv0TmFZsbJEAm8f7PItnoFQFE8kZJ3xeJmff7t5wQBOA9pXH
        """.replace("\n", "")
        # 获取参数变量
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/initDc"),
            headers=headers,
            data={"_json_att": ""}
        )
        token_result = re.search(r"var globalRepeatSubmitToken\s=\s\'(\w+)\'", response.text)
        key_check_is_change_result = re.search(r"\'key_check_isChange\':\'(\w+)\'", response.text)
        left_ticket_str_result = re.search(r"\'leftTicketStr\':\'([\w\%]+)\'", response.text)
        if not token_result or not key_check_is_change_result or not left_ticket_str_result:
            time_print("未通过乘客初始信息校验")
            return
        token = token_result.group(1)
        key_check_is_change = key_check_is_change_result.group(1)
        left_ticket_str = left_ticket_str_result.group(1)
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/getPassengerDTOs"),
            headers=headers,
            data=data
        )
        passengers = response.json().get("data", dict()).get("normal_passengers", list())
        cur_passengers = [
            passenger for passenger in passengers if passenger.get("passenger_name") in selected_passengers]
        sep = ","
        passenger_ticket_str = urllib.parse.quote(
            sep.join([sep.join((SEAT_MAP.get(seat_type), "0", TICKET_MAP.get(ticket_type),
                                cur_passenger.get("passenger_name"), "1",
                                cur_passenger.get("passenger_id_no"),
                                cur_passenger.get("mobile_no"), cur_passenger.get("allEncStr")))
                      for cur_passenger in cur_passengers]))
        old_passenger_str = urllib.parse.quote(sep.join([sep.join((cur_passenger.get("passenger_name"),
                                                                   cur_passenger.get("passenger_id_type_code"),
                                                                   cur_passenger.get("passenger_id_no"),
                                                                   cur_passenger.get("passenger_type") + "_")) for
                                                         cur_passenger in cur_passengers]))
        params = {
            "cancel_flag": "2",
            "bed_level_order_num": "000000000000000000000000000000",
            # 座位类型,0,车票类型,姓名,1,身份证号,电话号码,N,乘客字典元素中的allEncStr(多个乘客的话用‘,’隔开)
            "passengerTicketStr": passenger_ticket_str,
            "oldPassengerStr": old_passenger_str,
            "tour_flag": "dc",
            "whatsSelect": "1",
            "sessionId": "",
            "sig": "",
            "scene": "nc_login",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": token
        }
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/checkOrderInfo"),
            headers=headers,
            data=urlencode(params))
        if response.json().get("httpstatus") != requests.status_codes.codes.ok:
            time_print(f"{sep.join(selected_passengers)}中有乘客信息不正确")
            return
        gmt_format = "%a %b %d %Y %H:%M:%S GMT 0800 (中国标准时间)"
        params = {
            # 例如Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
            "train_date": pd.to_datetime(start_date).strftime(gmt_format),
            "train_no": train_info.get("train_no"),
            "stationTrainCode": train_info.get("train_code"),
            "seatType": SEAT_MAP.get(seat_type),  # 席别
            "fromStationTelecode": train_info.get("from_station_telecode"),
            "toStationTelecode": train_info.get("to_station_telecode"),
            "leftTicket": train_info.get("yp_info"),
            "purpose_codes": '00',
            "train_location": train_info.get("location_code"),
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": token
        }
        self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/getQueueCount"),
            headers=headers,
            data=urlencode(params)
        )
        params = {
            "passengerTicketStr": passenger_ticket_str,
            "oldPassengerStr": old_passenger_str,
            "purpose_codes": "00",
            "key_check_isChange": key_check_is_change,
            "leftTicketStr": left_ticket_str,
            "train_location": train_info.get("location_code"),
            "choose_seats": "",
            "seatDetailType": "000",
            "is_jy": "N",
            "is_cj": "Y",
            "encryptedData": encrypt_data,
            "whatsSelect": "1",
            "roomType": "00",
            "dwAll": "N",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": token
        }
        self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/confirmSingleForQueue"),
            headers=headers,
            data=urlencode(params),
        )
        params = {
            # 当前时间戳
            # 'random': '1713714595217',
            'random': round(time.time() * 1000),
            'tourFlag': 'dc',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        while True:
            response = self._session.get(
                urljoin(self._base_url, "otn/confirmPassenger/queryOrderWaitTime"),
                params=params,
                headers=headers,
            )
            # {
            # 	"validateMessagesShowId": "_validatorMessage",
            # 	"status": true,
            # 	"httpstatus": 200,
            # 	"data": {
            # 		"queryOrderWaitTimeStatus": true,
            # 		"count": 0,
            # 		"waitTime": -1,
            # 		"requestId": 7187839780614394060,
            # 		"waitCount": 0,
            # 		"tourFlag": "dc",
            # 		"orderId": "E411857572"
            # 	},
            # 	"messages": [],
            # 	"validateMessages": {}
            # }
            order_id = response.json().get("data", dict()).get("orderId")
            if order_id:
                break
        data = {
            'orderSequence_no': order_id,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        # {
        # 	"validateMessagesShowId": "_validatorMessage",
        # 	"status": true,
        # 	"httpstatus": 200,
        # 	"data": {
        # 		"submitStatus": true
        # 	},
        # 	"messages": [],
        # 	"validateMessages": {}
        # }
        response = self._session.post(
            urljoin(self._base_url, "otn/confirmPassenger/resultOrderForDcQueue"),
            headers=headers,
            data=data,
        )
        if response.json().get("data", dict()).get("submitStatus"):
            time_print("抢票成功")

    @staticmethod
    def _params_to_query_data(params: dict[str, str]) -> str:
        return "&".join([f"{k}={v}" for k, v in params.items()])

    def is_cookie_alive(self, headers: dict[str, str]) -> bool:
        response = self._session.post(
            url=urljoin(self._base_url, "passport/web/auth/uamtk"),
            headers=headers,
            verify=False,
            data={'appid': 'otn'}
        )
        return response.json().get("result_message") == "验证通过"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Host": "kyfw.12306.cn",
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": UserAgent().chrome,
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://kyfw.12306.cn/otn/resources/login.html",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }

    def run(self):
        from_, to, start_date = "深圳北", "武汉", "2024-05-01"
        headers = self.headers
        if not self.is_cookie_alive(headers):
            self._login("123456789", "4654644", "78797", headers)
        df_train_infos = self._query_left_tickets(from_, to, start_date, headers)
        for item in df_train_infos.itertuples():
            train_info = getattr(item, "_asdict")()
            self._choose_train(headers, from_, to, train_info)
            self._submit(start_date, headers, train_info)
