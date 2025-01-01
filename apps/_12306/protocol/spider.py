import re
import json
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from operator import itemgetter
from dataclasses import dataclass

import pandas as pd
from requests import utils as request_utils
from requests.cookies import RequestsCookieJar

from utils.common import time_print
from apps._12306.constants import SITE_MAP, SEAT_MAP, TICKET_MAP
from apps._12306.protocol.util import generate_unicode_url_encoded_string
from apps._12306.protocol.services import session, LoginAPI, QueryAPI, OrderAPI
from apps._12306.protocol.exceptions import InvalidTrainCodeError, QueryOrderError
from apps._12306.protocol.constants import ResponseCodes, LoginMethods, TICKETS_TABLE_COLUMNS

BASE_DIR = Path(__file__).parent.parent.parent.parent
SITE_MAP_REVERSE = {site_en_name: site_cn_name for site_cn_name, site_en_name in SITE_MAP.items()}

RESULT_CODE = "result_code"
TRAIN_NO = "train_no"
TRAIN_CODE = "train_code"
FROM_STATION_NAME = "from_station_name"
FROM_STATION_TELECODE = "from_station_telecode"
TO_STATION_NAME = "to_station_name"
TO_STATION_TELECODE = "to_station_telecode"
YP_INFO = "yp_info"
LOCATION_CODE = "location_code"
CAN_WEB_BY = "can_web_by"
PASSENGER_NAME = "passenger_name"
PASSENGER_ID_NO = "passenger_id_no"
MOBILE_NO = "mobile_no"
ALL_ENC_STR = "allEncStr"
PASSENGER_TYPE = "passenger_type"
PASSENGER_ID_TYPE_CODE = "passenger_id_type_code"
GMT_FORMAT = "%a %b %d %Y %H:%M:%S GMT 0800 (中国标准时间)"


@dataclass
class UserParams:
    # login params
    tp: str
    user_name: str
    password: str
    cast_num: str

    # query params
    train_date: str
    from_station_name: str
    to_station_name: str

    train_code: str
    selected_passengers: list[str]
    seat_type: str
    ticket_type: str


class TicketProcessor:

    def __init__(self) -> None:
        self.load_cookies()
        self._login = LoginAPI()
        self._query_api = QueryAPI()
        self._order = OrderAPI()
        self._uamtk = None
        self._newapptk = None
        self._headers = {
            'Host': 'kyfw.12306.cn',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://kyfw.12306.cn',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    @staticmethod
    def load_cookies() -> None:
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
            session.cookies = jar
        except json.decoder.JSONDecodeError as _:
            time_print("cookie文件有误，重新登陆获取cookie")

    @staticmethod
    def save_cookies() -> None:
        cookies = request_utils.dict_from_cookiejar(session.cookies)
        cookies_dir = Path(BASE_DIR) / "apps" / "_12306" / "preserve"
        cookies_dir.mkdir(exist_ok=True)
        cookie_file_path = cookies_dir / "cookies.txt"
        with open(cookie_file_path, "w") as f:
            json.dump(cookies, f)

    def _login_by_qr_code(self) -> dict[str, str]:
        uuid_ = self._login.create_qr64(self._headers)
        while True:
            results = self._login.check_qr(uuid_=uuid_, headers=self._headers)
            time_print("请扫描二维码")
            time.sleep(2)
            if results.get(RESULT_CODE) == ResponseCodes.LOGIN_SUCCESS.value:
                self._uamtk = results.get("uamtk")
                break
        return results

    def _login_by_pwd(self, user_name: str = None, password: str = None, cast_num: str = None) -> dict[str, str]:
        self._login.check_login_verify(user_name, self._headers)
        sms_code = self._login.get_sms_code(user_name, cast_num, self._headers)
        while True:
            results = self._login.web_login(user_name, password, sms_code, self._headers)
            if results.get(RESULT_CODE) != ResponseCodes.SUCCESS.value:
                sms_code = input("请输入手机验证码")
            else:
                break
        return results

    def _query_order_wait(self, repeat_submit_token: str) -> None:
        params = {
            "random": "",
            "tourFlag": "dc",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": repeat_submit_token,
        }
        valid_pre_wait, valid_cur_wait = 4, -1
        pre_wait = cur_wait = -100
        while True:
            if pre_wait == valid_pre_wait and cur_wait == valid_cur_wait:
                break
            if pre_wait == cur_wait == -4:
                raise QueryOrderError("提交订票信息失败")
            params["random"] = str(int(time.time() * 1000))
            result = self._order.query_order_wait_time(self._headers, params)
            pre_wait = cur_wait
            cur_wait = result.get("data", dict()).get("waitTime")

    def login(self, tp: LoginMethods = None, user_name: str = None, password: str = None, cast_num: str = None) -> None:
        if self._login.is_cookie_alive(self._headers):
            return
        tp = tp.value if tp else LoginMethods.QR_CODE.value
        if tp == LoginMethods.QR_CODE.value:
            self._login_by_qr_code()
        else:
            self._login_by_pwd(user_name, password, cast_num)
        self._login.otn_user_login(self._headers)
        tk_json = self._login.auth_uamtk(self._headers)
        self._newapptk = tk_json.get("newapptk")
        self._login.uam_auth_client(self._headers, self._newapptk)
        self._login.otn_user_login2(self._headers)
        self._login.otn_login_conf(self._headers)
        self._login.init_my_12306(self._headers)
        self.save_cookies()

    def query_left_tickets(self, train_date: str, from_station: str, to_station: str) -> pd.DataFrame:
        r = self._query_api.query_trains(train_date, from_station, to_station, self._headers)
        self._query_api.lc_query_g(train_date, from_station, to_station, self._newapptk, self._headers)
        results = r.get("data", dict()).get("result", list())
        station_map = r.get("data", dict()).get("map", dict())
        filter_data_rule = itemgetter(*[*list(range(40)), 46, *list(range(48, 52)), *list(range(53, 56))])
        data = [filter_data_rule(result.split("|")) for result in results]
        df = pd.DataFrame(data=data, columns=TICKETS_TABLE_COLUMNS)
        df[FROM_STATION_NAME] = df[FROM_STATION_TELECODE].map(station_map)
        station_map_reversed = {v: k for k, v in station_map.items()}
        df[TO_STATION_NAME] = df[TO_STATION_TELECODE].map(station_map)
        time_print("查询完毕")
        # 补齐cookie信息
        cookies_value = {
            '_jc_save_fromDate': train_date,
            '_jc_save_showIns': 'true',
            '_jc_save_toDate': datetime.now().strftime("%Y-%m-%d"),
            '_jc_save_fromStation': f'{generate_unicode_url_encoded_string(from_station).upper()}%2C{station_map_reversed.get(from_station)}',
            '_jc_save_toStation': f'{generate_unicode_url_encoded_string(to_station).upper()}%2C{station_map_reversed.get(to_station)}',
        }
        for k, v in cookies_value.items():
            request_utils.add_dict_to_cookiejar(session.cookies, {k: v})
        return df

    def submit_tickets(self, df_tickets: pd.DataFrame, params: UserParams) -> None:
        df_train = df_tickets[df_tickets[TRAIN_CODE] == params.train_code]
        if df_train.empty:
            raise InvalidTrainCodeError(f"没有‘{params.train_code}’车次")

        def _extract(pattern: str, content: str) -> str:
            result = re.search(pattern, content)
            if result is None:
                return ""
            return result.groups()[0]

        train_info = df_train.to_dict(orient="records")[0]
        secret_string = train_info.get("secret_str")
        data = {
            'back_train_date': datetime.now().strftime("%Y-%m-%d"),
            'bed_level_info': '',
            'purpose_codes': 'ADULT',
            'query_from_station_name': params.from_station_name,
            'query_to_station_name': params.to_station_name,
            'seat_discount_info': '90090',
            'secretStr': secret_string,
            'tour_flag': 'dc',
            'train_date': params.train_date
        }
        self._query_api.submit_order_request(data, self._headers)
        text = self._order.confirm_passenger_init_dc(self._headers)

        # 提取 globalRepeatSubmitToken, key_check_isChange, leftTicketStr
        repeat_submit_token = _extract(r"var globalRepeatSubmitToken\s=\s\'(\w+)\'", text)
        passengers = self._order.get_passenger_dtos(self._headers, repeat_submit_token)
        cur_passengers = [
            passenger for passenger in passengers if passenger.get(PASSENGER_NAME) in params.selected_passengers]
        sep = ","
        passenger_ticket_str = quote(
            sep.join(
                [
                    sep.join(
                        (
                            SEAT_MAP.get(params.seat_type),
                            "0",
                            TICKET_MAP.get(params.ticket_type),
                            cur_passenger.get(PASSENGER_NAME),
                            "1",
                            cur_passenger.get(PASSENGER_ID_NO),
                            cur_passenger.get(MOBILE_NO),
                            cur_passenger.get(ALL_ENC_STR)
                        )
                    ) for cur_passenger in cur_passengers
                ]
            )
        )
        old_passenger_str = quote(
            sep.join(
                [
                    sep.join(
                        (
                            cur_passenger.get(PASSENGER_NAME),
                            cur_passenger.get(PASSENGER_ID_TYPE_CODE),
                            cur_passenger.get(PASSENGER_ID_NO),
                            cur_passenger.get(PASSENGER_TYPE) + "_"
                        )
                    ) for cur_passenger in cur_passengers
                ]
            )
        )
        check_order_data = {
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
            '_json_att': '',
            'bed_level_order_num': '000000000000000000000000000000',
            'cancel_flag': '2',
            'oldPassengerStr': old_passenger_str,
            # 座位类型,0,车票类型,姓名,1,身份证号,电话号码,N,乘客字典元素中的allEncStr(多个乘客的话用‘,’隔开)
            'passengerTicketStr': passenger_ticket_str,
            'scene': 'nc_login',
            'sessionId': '',
            'sig': '',
            'tour_flag': 'dc',
            'whatsSelect': '1'
        }
        self._order.check_order_info(self._headers, check_order_data)
        key_check_is_change = _extract(r"\'key_check_isChange\':\'(\w+)\'", text)
        time_print(f"key_check_is_change: {key_check_is_change}")
        left_ticket_str = _extract(r"\'leftTicketStr\':\'([\w\%]+)\'", text)
        time_print(f"left_ticket_str:{left_ticket_str}")
        queue_count_data = {
            # 例如Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
            "train_date": pd.to_datetime(params.train_date).strftime(GMT_FORMAT),
            "train_no": df_train.get(TRAIN_NO),
            "stationTrainCode": train_info.get(TRAIN_CODE),
            "seatType": SEAT_MAP.get(params.seat_type),  # 席别
            "fromStationTelecode": train_info.get(FROM_STATION_TELECODE),
            "toStationTelecode": train_info.get(TO_STATION_TELECODE),
            "leftTicket": train_info.get(YP_INFO),
            "purpose_codes": '00',
            "train_location": train_info.get(LOCATION_CODE),
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": repeat_submit_token
        }
        self._order.get_queue_count(self._headers, queue_count_data)
        confirm_single_data = {
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
            '_json_att': '',
            'choose_seats': '',
            'dwAll': 'N',
            # todo 可能需要加密逆向
            'encryptedData': '',
            'is_cj': 'Y',
            'is_jy': 'N',
            'key_check_isChange': key_check_is_change,
            'leftTicketStr': left_ticket_str,
            'oldPassengerStr': old_passenger_str,
            'passengerTicketStr': passenger_ticket_str,
            'purpose_codes': '00',
            'roomType': '00',
            'seatDetailType': '000',
            'train_location': 'P4',
            'whatsSelect': '1'
        }
        self._order.confirm_for_single_queue(self._headers, confirm_single_data)
        base_data = {
            'type': 'dc',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
        }
        self._order.otn_base_data_log(self._headers, base_data)
        self._query_order_wait(repeat_submit_token)

    def process(self, params: UserParams) -> None:
        self.login(
            LoginMethods(params.tp),
            user_name=params.user_name,
            password=params.password,
            cast_num=params.cast_num
        )
        while True:
            df_tickets = self.query_left_tickets(
                params.train_date,
                params.from_station_name,
                params.to_station_name
            )
            df_can_buy_tickets = df_tickets[df_tickets[CAN_WEB_BY] == "Y"]
            if not df_can_buy_tickets.empty:
                break
        start = time.perf_counter()
        self.submit_tickets(df_can_buy_tickets, params)
        time_print(f"抢票总共耗时{time.perf_counter() - start}秒")


if __name__ == "__main__":
    tp_processor = TicketProcessor()
    p = UserParams(
        tp="QR_CODE",
        user_name="",
        password="",
        cast_num="",
        train_date="2025-01-10",
        from_station_name="北京",
        to_station_name="广州",
        train_code="G337",
        selected_passengers=[""],
        seat_type="二等座",
        ticket_type="成人票",
    )
    tp_processor.process(p)
